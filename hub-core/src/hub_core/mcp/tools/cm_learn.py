"""MCP Tool: cm_learn - Learn sync.

Tool 6 of 8: Initiate, review, accept, and apply learnings.
"""

from typing import Optional, Dict, Any, List

from fastmcp import FastMCP

from ...domain.services.learn_service import LearnService
from ..decorators import handle_mcp_errors


def register_cm_learn(
    mcp: FastMCP,
    learn_service: LearnService,
):
    """Register cm_learn tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        learn_service: LearnService instance
    """
    
    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_learn(
        action: str,
        feature_name: Optional[str] = None,
        proposal_id: Optional[str] = None,
        data: Optional[dict] = None,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Manage learning sync: capture and apply learnings from feature execution.
        
        Consolidates the Learn phase of Intent → Build → Learn workflow.
        
        Args:
            action: Action to perform:
                - "initiate": Start learning sync for a completed feature
                - "review": Review a learning proposal
                - "accept": Accept specific learnings from a proposal
                - "apply": Apply accepted learnings to context (requires confirm=True)
            feature_name: Feature name for "initiate" action
            proposal_id: Proposal ID for "review", "accept", "apply" actions
            data: Additional data for actions:
                - For "initiate": {changed_files, test_results, execution_transcript, user_feedback}
                - For "accept": {learning_ids, context_update_indices, accept_changelog}
                - For "apply": {learning_ids, context_update_indices, apply_changelog}
            confirm: Required True for "apply" action (destructive operation)
        
        Returns:
            Dictionary with operation result:
            - For "initiate": learning proposal with outcomes and drafts
            - For "review": full proposal details
            - For "accept": preview of what would be applied
            - For "apply": result of applying learnings
        
        Examples:
            # Start learning sync
            cm_learn(action="initiate", feature_name="F001", data={
                "changed_files": ["src/api.py"],
                "user_feedback": "Implementation went smoothly"
            })
            
            # Review a proposal
            cm_learn(action="review", proposal_id="learn-123")
            
            # Apply learnings
            cm_learn(action="apply", proposal_id="learn-123", confirm=True)
        """
        valid_actions = ["initiate", "review", "accept", "apply"]
        if action not in valid_actions:
            return {"error": f"Invalid action: {action}", "valid_actions": valid_actions}
        
        # ====================================================================
        # ACTION: INITIATE
        # ====================================================================
        if action == "initiate":
            if not feature_name:
                return {"error": "Feature name required for initiate action"}
            
            data = data or {}
            proposal = learn_service.initiate_learn_sync(
                feature_name=feature_name,
                changed_files=data.get("changed_files"),
                test_results=data.get("test_results"),
                execution_transcript=data.get("execution_transcript"),
                user_feedback=data.get("user_feedback"),
            )
            
            return {
                "action": "initiate",
                "proposal_id": proposal.proposal_id,
                "feature_name": proposal.feature_name,
                "created_at": proposal.created_at,
                "outcome_summary": {
                    "what_implemented": proposal.outcome_summary.what_implemented,
                    "what_failed": proposal.outcome_summary.what_failed,
                    "unexpected_difficulties": proposal.outcome_summary.unexpected_difficulties,
                    "discovered_constraints": proposal.outcome_summary.discovered_constraints,
                },
                "learning_drafts": [
                    {
                        "learning_id": draft.learning_id,
                        "type": draft.artifact_type.value,
                        "title": draft.title,
                        "confidence": draft.confidence.value,
                        "impact": draft.impact.value,
                    }
                    for draft in proposal.learning_drafts
                ],
                "context_updates": [
                    {
                        "artifact_type": update.artifact_type,
                        "artifact_path": update.artifact_path,
                        "update_type": update.update_type,
                        "rationale": update.rationale,
                    }
                    for update in proposal.context_updates
                ],
                "changelog_entry": {
                    "date": proposal.changelog_entry.date,
                    "what_changed": proposal.changelog_entry.what_changed,
                    "why_changed": proposal.changelog_entry.why_changed,
                } if proposal.changelog_entry else None,
                "next_step": f"Use cm_learn(action='review', proposal_id='{proposal.proposal_id}') to review details",
            }
        
        # ====================================================================
        # ACTION: REVIEW
        # ====================================================================
        elif action == "review":
            if not proposal_id:
                return {"error": "Proposal ID required for review action"}
            
            proposal = learn_service.get_proposal(proposal_id)
            
            return {
                "action": "review",
                "proposal_id": proposal.proposal_id,
                "feature_name": proposal.feature_name,
                "learning_drafts": [
                    {
                        "learning_id": draft.learning_id,
                        "type": draft.artifact_type.value,
                        "title": draft.title,
                        "context": draft.context,
                        "recommendation": draft.recommendation,
                        "evidence": draft.evidence,
                        "confidence": draft.confidence.value,
                        "impact": draft.impact.value,
                    }
                    for draft in proposal.learning_drafts
                ],
                "context_updates": [
                    {
                        "artifact_type": update.artifact_type,
                        "artifact_path": update.artifact_path,
                        "update_type": update.update_type,
                        "proposed_content": update.proposed_content[:200] + "..." if len(update.proposed_content) > 200 else update.proposed_content,
                        "rationale": update.rationale,
                    }
                    for update in proposal.context_updates
                ],
            }
        
        # ====================================================================
        # ACTION: ACCEPT (placeholder)
        # ====================================================================
        elif action == "accept":
            return {
                "error": "Accept not yet fully implemented",
                "tip": "Use 'apply' to apply all learnings from a proposal",
            }
        
        # ====================================================================
        # ACTION: APPLY (placeholder - requires file writes)
        # ====================================================================
        elif action == "apply":
            if not proposal_id:
                return {"error": "Proposal ID required for apply action"}
            if not confirm:
                return {
                    "error": "Apply is a destructive operation. Set confirm=True to proceed.",
                    "warning": "This will modify context files based on the learning proposal.",
                }
            
            return {
                "error": "Apply not yet fully implemented",
                "tip": "Manually apply learnings by creating/updating files based on proposal",
            }
