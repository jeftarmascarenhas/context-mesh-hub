"""Repository for LearningProposal persistence."""

from typing import List, Optional
from dataclasses import asdict

from ...domain.models.learn import (
    LearningProposal,
    OutcomeSummary,
    LearningDraft,
    ContextUpdateProposal,
    ChangelogEntryProposal,
    LearningArtifactType,
    ConfidenceLevel,
    ImpactLevel,
)
from ...shared.errors import ArtifactNotFoundError
from .file_store import FileStore


class ProposalRepository:
    """Repository for managing LearningProposal persistence."""
    
    def __init__(self, store: FileStore):
        """Initialize repository.
        
        Args:
            store: FileStore instance for persistence.
        """
        self.store = store
    
    def save_proposal(self, proposal: LearningProposal) -> None:
        """Save learning proposal.
        
        Args:
            proposal: LearningProposal to save.
        """
        data = self._proposal_to_dict(proposal)
        self.store.save(f"proposal_{proposal.proposal_id}", data)
    
    def load_proposal(self, proposal_id: str) -> Optional[LearningProposal]:
        """Load learning proposal by ID.
        
        Args:
            proposal_id: Proposal identifier.
            
        Returns:
            LearningProposal if found, None otherwise.
        """
        data = self.store.load(f"proposal_{proposal_id}")
        if not data:
            return None
        
        return self._dict_to_proposal(data)
    
    def get_proposal(self, proposal_id: str) -> LearningProposal:
        """Get learning proposal by ID (raises if not found).
        
        Args:
            proposal_id: Proposal identifier.
            
        Returns:
            LearningProposal instance.
            
        Raises:
            ArtifactNotFoundError: If proposal not found.
        """
        proposal = self.load_proposal(proposal_id)
        if not proposal:
            raise ArtifactNotFoundError("LearningProposal", proposal_id)
        return proposal
    
    def list_proposals(self) -> List[LearningProposal]:
        """List all proposals.
        
        Returns:
            List of LearningProposal instances.
        """
        keys = [k for k in self.store.list_keys() if k.startswith("proposal_")]
        proposals = []
        
        for key in keys:
            data = self.store.load(key)
            if data:
                proposals.append(self._dict_to_proposal(data))
        
        return proposals
    
    def delete_proposal(self, proposal_id: str) -> None:
        """Delete learning proposal.
        
        Args:
            proposal_id: Proposal identifier.
        """
        self.store.delete(f"proposal_{proposal_id}")
    
    def _proposal_to_dict(self, proposal: LearningProposal) -> dict:
        """Convert LearningProposal to dict for serialization."""
        data = asdict(proposal)
        
        # Convert enums to strings in learning_drafts
        if 'learning_drafts' in data:
            for draft in data['learning_drafts']:
                draft['artifact_type'] = draft['artifact_type'].value if hasattr(draft['artifact_type'], 'value') else draft['artifact_type']
                draft['confidence'] = draft['confidence'].value if hasattr(draft['confidence'], 'value') else draft['confidence']
                draft['impact'] = draft['impact'].value if hasattr(draft['impact'], 'value') else draft['impact']
        
        return data
    
    def _dict_to_proposal(self, data: dict) -> LearningProposal:
        """Convert dict to LearningProposal."""
        # Reconstruct OutcomeSummary
        outcome_data = data.get('outcome_summary', {})
        outcome = OutcomeSummary(**outcome_data)
        
        # Reconstruct LearningDrafts
        drafts_data = data.get('learning_drafts', [])
        drafts = []
        for draft_data in drafts_data:
            # Convert string enums back to Enum objects
            draft_data['artifact_type'] = LearningArtifactType(draft_data['artifact_type'])
            draft_data['confidence'] = ConfidenceLevel(draft_data['confidence'])
            draft_data['impact'] = ImpactLevel(draft_data['impact'])
            drafts.append(LearningDraft(**draft_data))
        
        # Reconstruct ContextUpdateProposals
        updates_data = data.get('context_updates', [])
        updates = [ContextUpdateProposal(**update_data) for update_data in updates_data]
        
        # Reconstruct ChangelogEntryProposal (optional)
        changelog_data = data.get('changelog_entry')
        changelog = ChangelogEntryProposal(**changelog_data) if changelog_data else None
        
        return LearningProposal(
            proposal_id=data['proposal_id'],
            feature_name=data['feature_name'],
            created_at=data['created_at'],
            outcome_summary=outcome,
            learning_drafts=drafts,
            context_updates=updates,
            changelog_entry=changelog,
        )
