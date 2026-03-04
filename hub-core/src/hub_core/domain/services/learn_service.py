"""Learn Service - Learning Sync workflow.

Pure business logic for Learn Sync: explicit learning and context evolution.
Delegates I/O to infrastructure layer (persistence).
"""

import uuid
import re
from datetime import datetime
from typing import Dict, List, Optional

from ...loader import ContextLoader
from ...infrastructure.persistence.proposal_repository import ProposalRepository
from ...infrastructure.parsers.markdown_parser import MarkdownParser
from ...shared.errors import ArtifactNotFoundError
from ..models.learn import (
    LearningArtifactType,
    ConfidenceLevel,
    ImpactLevel,
    OutcomeSummary,
    LearningDraft,
    ContextUpdateProposal,
    ChangelogEntryProposal,
    LearningProposal,
)


class LearnService:
    """Service for Learn Sync workflow.
    
    Handles:
    - Outcome collection from feature execution
    - Learning classification (patterns, anti-patterns, constraints, etc.)
    - Context update proposals (feature intents, decisions, patterns)
    - Changelog entry generation
    
    All proposals are persisted via ProposalRepository.
    """
    
    def __init__(
        self,
        loader: ContextLoader,
        proposal_repository: ProposalRepository,
        parser: MarkdownParser,
    ):
        """Initialize learn service with dependencies.
        
        Args:
            loader: ContextLoader for accessing artifacts
            proposal_repository: ProposalRepository for persisting proposals
            parser: MarkdownParser for extracting markdown sections
        """
        self.loader = loader
        self.proposal_repo = proposal_repository
        self.parser = parser
    
    # ========================================================================
    # OUTCOME COLLECTION
    # ========================================================================
    
    def collect_outcomes(
        self,
        feature_name: str,
        build_plan_id: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
        test_results: Optional[str] = None,
        execution_transcript: Optional[str] = None,
        user_feedback: Optional[str] = None,
    ) -> OutcomeSummary:
        """Collect execution outcomes from build.
        
        Args:
            feature_name: Feature ID or name
            build_plan_id: Optional build plan ID
            changed_files: List of changed file paths
            test_results: Test results summary
            execution_transcript: Execution transcript
            user_feedback: User-provided feedback
        
        Returns:
            OutcomeSummary instance
        """
        summary = OutcomeSummary()
        
        # Collect from changed files
        if changed_files:
            summary.evidence_files = changed_files
            summary.what_implemented.append(f"Modified {len(changed_files)} file(s)")
        
        # Collect from test results
        if test_results:
            summary.evidence_logs.append("Test results provided")
            if "failed" in test_results.lower() or "error" in test_results.lower():
                summary.what_failed.append("Some tests failed")
            elif "passed" in test_results.lower():
                summary.what_implemented.append("Tests passed")
        
        # Collect from execution transcript
        if execution_transcript:
            summary.evidence_logs.append("Execution transcript provided")
            if "error" in execution_transcript.lower():
                summary.what_failed.append("Errors encountered during execution")
            if "unexpected" in execution_transcript.lower():
                summary.unexpected_difficulties.append(
                    "Unexpected issues mentioned in transcript"
                )
        
        # Collect from user feedback
        if user_feedback:
            self._parse_user_feedback(user_feedback, summary)
        
        # If no evidence provided, mark as unknown
        if not (changed_files or test_results or execution_transcript or user_feedback):
            summary.unknowns.append(
                "No execution evidence provided. Please provide changed files, "
                "test results, execution transcript, or user feedback."
            )
        
        return summary
    
    def _parse_user_feedback(self, user_feedback: str, summary: OutcomeSummary) -> None:
        """Parse user feedback into outcome categories.
        
        Args:
            user_feedback: User feedback text
            summary: OutcomeSummary to populate
        """
        lines = user_feedback.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                line = line[1:].strip()
                
                if "failed" in line.lower() or "error" in line.lower():
                    summary.what_failed.append(line)
                elif "difficult" in line.lower() or "hard" in line.lower():
                    summary.unexpected_difficulties.append(line)
                elif "assumption" in line.lower() or "wrong" in line.lower():
                    summary.wrong_assumptions.append(line)
                elif "constraint" in line.lower():
                    summary.discovered_constraints.append(line)
                else:
                    summary.what_implemented.append(line)
    
    # ========================================================================
    # LEARNING CLASSIFICATION
    # ========================================================================
    
    def classify_learnings(
        self,
        outcome_summary: OutcomeSummary,
        feature_name: str,
    ) -> List[LearningDraft]:
        """Classify outcomes into learning artifacts.
        
        Args:
            outcome_summary: OutcomeSummary instance
            feature_name: Feature ID or name
        
        Returns:
            List of LearningDraft instances
        """
        drafts = []
        learning_counter = 0
        
        # Get feature intent for context
        feature = self.loader.get_feature_intent(feature_name)
        related_decisions = []
        if feature:
            related_decisions = self.parser.extract_decision_links(feature["content"])
        
        # Classify failures as anti-patterns or risk annotations
        for failure in outcome_summary.what_failed:
            learning_counter += 1
            drafts.append(LearningDraft(
                learning_id=f"learning-{learning_counter}",
                artifact_type=LearningArtifactType.ANTI_PATTERN,
                title=f"Failure: {failure[:50]}",
                context=f"During implementation of {feature_name}, the following failure occurred.",
                evidence=outcome_summary.evidence_files + outcome_summary.evidence_logs,
                recommendation=f"Avoid this approach: {failure}",
                related_intents=[feature_name],
                related_decisions=related_decisions,
                confidence=ConfidenceLevel.HIGH,
                impact=ImpactLevel.MEDIUM,
            ))
        
        # Classify unexpected difficulties as constraints or risks
        for difficulty in outcome_summary.unexpected_difficulties:
            learning_counter += 1
            drafts.append(LearningDraft(
                learning_id=f"learning-{learning_counter}",
                artifact_type=LearningArtifactType.CONSTRAINT_DISCOVERY,
                title=f"Constraint: {difficulty[:50]}",
                context=f"During implementation of {feature_name}, unexpected difficulty was encountered.",
                evidence=outcome_summary.evidence_files + outcome_summary.evidence_logs,
                recommendation=f"Consider this constraint in future planning: {difficulty}",
                related_intents=[feature_name],
                related_decisions=related_decisions,
                confidence=ConfidenceLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
            ))
        
        # Classify wrong assumptions as decision updates or evolution notes
        for assumption in outcome_summary.wrong_assumptions:
            learning_counter += 1
            drafts.append(LearningDraft(
                learning_id=f"learning-{learning_counter}",
                artifact_type=LearningArtifactType.DECISION_UPDATE,
                title=f"Assumption Correction: {assumption[:50]}",
                context=f"During implementation of {feature_name}, an assumption was found to be incorrect.",
                evidence=outcome_summary.evidence_files + outcome_summary.evidence_logs,
                recommendation=f"Review related decisions and update if needed: {assumption}",
                related_intents=[feature_name],
                related_decisions=related_decisions,
                confidence=ConfidenceLevel.HIGH,
                impact=ImpactLevel.HIGH,
            ))
        
        # Classify discovered constraints
        for constraint in outcome_summary.discovered_constraints:
            learning_counter += 1
            drafts.append(LearningDraft(
                learning_id=f"learning-{learning_counter}",
                artifact_type=LearningArtifactType.CONSTRAINT_DISCOVERY,
                title=f"New Constraint: {constraint[:50]}",
                context=f"During implementation of {feature_name}, a new constraint was discovered.",
                evidence=outcome_summary.evidence_files + outcome_summary.evidence_logs,
                recommendation=f"Document this constraint: {constraint}",
                related_intents=[feature_name],
                related_decisions=related_decisions,
                confidence=ConfidenceLevel.HIGH,
                impact=ImpactLevel.MEDIUM,
            ))
        
        # Classify successful implementations as patterns (if significant)
        if self._is_significant_implementation(outcome_summary):
            learning_counter += 1
            drafts.append(LearningDraft(
                learning_id=f"learning-{learning_counter}",
                artifact_type=LearningArtifactType.PATTERN,
                title=f"Implementation Pattern: {feature_name}",
                context=f"Successful implementation approach for {feature_name}.",
                evidence=outcome_summary.evidence_files + outcome_summary.evidence_logs,
                recommendation="Consider reusing this approach for similar features.",
                related_intents=[feature_name],
                related_decisions=related_decisions,
                confidence=ConfidenceLevel.MEDIUM,
                impact=ImpactLevel.LOW,
            ))
        
        return drafts
    
    def _is_significant_implementation(self, outcome_summary: OutcomeSummary) -> bool:
        """Check if implementation is significant enough for pattern creation.
        
        Args:
            outcome_summary: OutcomeSummary instance
        
        Returns:
            True if significant, False otherwise
        """
        if not outcome_summary.what_implemented:
            return False
        
        # Significant if 3+ items implemented
        if len(outcome_summary.what_implemented) >= 3:
            return True
        
        # Significant if mentions pattern/approach
        return any(
            "pattern" in impl.lower() or "approach" in impl.lower()
            for impl in outcome_summary.what_implemented
        )
    
    # ========================================================================
    # CONTEXT UPDATE PROPOSALS
    # ========================================================================
    
    def propose_context_updates(
        self,
        outcome_summary: OutcomeSummary,
        learning_drafts: List[LearningDraft],
        feature_name: str,
    ) -> List[ContextUpdateProposal]:
        """Propose updates to context artifacts.
        
        Args:
            outcome_summary: OutcomeSummary instance
            learning_drafts: List of LearningDraft instances
            feature_name: Feature ID or name
        
        Returns:
            List of ContextUpdateProposal instances
        """
        proposals = []
        
        # Get feature intent
        feature = self.loader.get_feature_intent(feature_name)
        if not feature:
            return proposals
        
        # Propose feature intent updates (implementation notes)
        implementation_notes = self._build_implementation_notes(outcome_summary)
        if implementation_notes:
            proposals.append(ContextUpdateProposal(
                artifact_type="feature_intent",
                artifact_path=feature["path"],
                update_type="add_implementation_notes",
                proposed_content=implementation_notes,
                rationale="Capture implementation outcomes and discovered limitations.",
            ))
        
        # Propose decision updates (for decision update learnings)
        decision_updates = [
            draft for draft in learning_drafts
            if draft.artifact_type == LearningArtifactType.DECISION_UPDATE
        ]
        
        for draft in decision_updates:
            for decision_num in draft.related_decisions:
                proposals.append(ContextUpdateProposal(
                    artifact_type="decision",
                    artifact_path=f"context/decisions/{decision_num}-*.md",
                    update_type="add_outcomes",
                    proposed_content=(
                        f"## Outcomes\n\n{draft.recommendation}\n\n"
                        f"**Evidence**: {', '.join(draft.evidence[:3])}\n"
                    ),
                    rationale=f"Learning from {feature_name} execution: {draft.title}",
                ))
        
        return proposals
    
    def _build_implementation_notes(self, outcome_summary: OutcomeSummary) -> str:
        """Build implementation notes section from outcomes.
        
        Args:
            outcome_summary: OutcomeSummary instance
        
        Returns:
            Markdown string with implementation notes
        """
        notes = []
        
        if outcome_summary.what_implemented:
            notes.append("## Implementation Notes\n")
            notes.append("### What Was Implemented\n")
            for item in outcome_summary.what_implemented:
                notes.append(f"- {item}\n")
        
        if outcome_summary.unexpected_difficulties or outcome_summary.discovered_constraints:
            notes.append("\n### Limitations / Edge Cases\n")
            for item in outcome_summary.unexpected_difficulties + outcome_summary.discovered_constraints:
                notes.append(f"- {item}\n")
        
        return "".join(notes)
    
    # ========================================================================
    # CHANGELOG PROPOSALS
    # ========================================================================
    
    def propose_changelog_entry(
        self,
        feature_name: str,
        outcome_summary: OutcomeSummary,
        learning_drafts: List[LearningDraft],
        context_updates: List[ContextUpdateProposal],
    ) -> ChangelogEntryProposal:
        """Propose changelog entry.
        
        Args:
            feature_name: Feature ID or name
            outcome_summary: OutcomeSummary instance
            learning_drafts: List of LearningDraft instances
            context_updates: List of ContextUpdateProposal instances
        
        Returns:
            ChangelogEntryProposal instance
        """
        # Get related decisions
        feature = self.loader.get_feature_intent(feature_name)
        related_decisions = []
        if feature:
            related_decisions = self.parser.extract_decision_links(feature["content"])
        
        # Build what changed
        what_changed = []
        if outcome_summary.what_implemented:
            what_changed.append(f"Implemented {feature_name} feature")
        if learning_drafts:
            what_changed.append(f"Generated {len(learning_drafts)} learning artifact(s)")
        if context_updates:
            what_changed.append(f"Proposed {len(context_updates)} context update(s)")
        
        # Build why changed
        why_changed = f"Learn Sync after {feature_name} execution. "
        if outcome_summary.what_implemented:
            why_changed += "Captured implementation outcomes. "
        if outcome_summary.what_failed or outcome_summary.unexpected_difficulties:
            why_changed += "Documented failures and difficulties for future reference. "
        
        # Get learning artifact IDs
        learning_artifact_ids = [draft.learning_id for draft in learning_drafts]
        
        return ChangelogEntryProposal(
            date=datetime.now().strftime("%Y-%m-%d"),
            what_changed=(
                "; ".join(what_changed) if what_changed else f"Learn Sync for {feature_name}"
            ),
            why_changed=why_changed.strip(),
            related_features=[feature_name],
            related_decisions=related_decisions,
            learning_artifacts=learning_artifact_ids,
        )
    
    # ========================================================================
    # LEARN SYNC WORKFLOW
    # ========================================================================
    
    def initiate_learn_sync(
        self,
        feature_name: str,
        changed_files: Optional[List[str]] = None,
        test_results: Optional[str] = None,
        execution_transcript: Optional[str] = None,
        user_feedback: Optional[str] = None,
    ) -> LearningProposal:
        """Initiate learn sync for a feature.
        
        Args:
            feature_name: Feature ID or name
            changed_files: List of changed file paths
            test_results: Test results summary
            execution_transcript: Execution transcript
            user_feedback: User-provided feedback
        
        Returns:
            LearningProposal instance
        """
        # Collect outcomes
        outcome_summary = self.collect_outcomes(
            feature_name=feature_name,
            changed_files=changed_files,
            test_results=test_results,
            execution_transcript=execution_transcript,
            user_feedback=user_feedback,
        )
        
        # Generate learning drafts
        learning_drafts = self.classify_learnings(outcome_summary, feature_name)
        
        # Propose context updates
        context_updates = self.propose_context_updates(
            outcome_summary, learning_drafts, feature_name
        )
        
        # Propose changelog entry
        changelog_entry = self.propose_changelog_entry(
            feature_name, outcome_summary, learning_drafts, context_updates
        )
        
        # Create proposal
        proposal_id = str(uuid.uuid4())
        proposal = LearningProposal(
            proposal_id=proposal_id,
            feature_name=feature_name,
            created_at=datetime.now().isoformat(),
            outcome_summary=outcome_summary,
            learning_drafts=learning_drafts,
            context_updates=context_updates,
            changelog_entry=changelog_entry,
        )
        
        # Persist proposal
        self.proposal_repo.save_proposal(proposal)
        
        return proposal
    
    def get_proposal(self, proposal_id: str) -> LearningProposal:
        """Get a learning proposal by ID.
        
        Args:
            proposal_id: Proposal ID
        
        Returns:
            LearningProposal instance
            
        Raises:
            ArtifactNotFoundError: If proposal not found
        """
        proposal = self.proposal_repo.get_proposal(proposal_id)
        if not proposal:
            raise ArtifactNotFoundError(
                f"Learning proposal not found: {proposal_id}",
                artifact_type="learning_proposal",
                artifact_name=proposal_id
            )
        return proposal
    
    def list_proposals(self) -> List[LearningProposal]:
        """List all learning proposals.
        
        Returns:
            List of LearningProposal instances
        """
        return self.proposal_repo.list_proposals()
    
    def delete_proposal(self, proposal_id: str) -> None:
        """Delete a learning proposal.
        
        Args:
            proposal_id: Proposal ID
            
        Raises:
            ArtifactNotFoundError: If proposal not found
        """
        proposal = self.proposal_repo.get_proposal(proposal_id)
        if not proposal:
            raise ArtifactNotFoundError(
                f"Learning proposal not found: {proposal_id}",
                artifact_type="learning_proposal",
                artifact_name=proposal_id
            )
        self.proposal_repo.delete_proposal(proposal_id)
