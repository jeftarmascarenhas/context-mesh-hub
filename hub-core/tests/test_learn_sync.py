"""Tests for Learn Sync functionality.

Updated for refactored architecture (v0.2.0).
Uses LearnService from domain/services instead of old learn_sync.py.
"""

import pytest
from pathlib import Path
import tempfile

from hub_core.domain.services.learn_service import LearnService
from hub_core.domain.models.learn import (
    LearningArtifactType,
    ConfidenceLevel,
    ImpactLevel,
    OutcomeSummary,
)
from hub_core.loader import ContextLoader
from hub_core.infrastructure.parsers.markdown_parser import MarkdownParser
from hub_core.infrastructure.persistence.file_store import FileStore
from hub_core.infrastructure.persistence.proposal_repository import ProposalRepository


@pytest.fixture
def learn_service():
    """Create LearnService with dependencies."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    loader.load()
    parser = MarkdownParser()
    
    # Use temp directory for persistence
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_store = FileStore(Path(tmp_dir))
        proposal_repo = ProposalRepository(file_store)
        
        yield LearnService(
            loader=loader,
            proposal_repository=proposal_repo,
            parser=parser,
        )


def test_learn_service_init(learn_service):
    """Test Learn Service initialization."""
    assert learn_service.loader is not None
    assert learn_service.proposal_repo is not None
    assert learn_service.parser is not None


def test_collect_outcomes(learn_service):
    """Test outcome collection."""
    outcome = learn_service.collect_outcomes(
        feature_name="test-feature",
        changed_files=["file1.py", "file2.ts"],
        test_results="All tests passed",
        user_feedback="- Implemented feature X\n- Failed to implement feature Y"
    )
    
    assert len(outcome.what_implemented) > 0
    assert len(outcome.evidence_files) == 2


def test_classify_learnings(learn_service):
    """Test learning classification."""
    outcome = OutcomeSummary(
        what_failed=["Test failure in module X"],
        unexpected_difficulties=["Unexpected complexity in Y"],
        wrong_assumptions=["Assumed Z would work"],
        discovered_constraints=["Constraint A discovered"]
    )
    
    drafts = learn_service.classify_learnings(outcome, "test-feature")
    
    assert len(drafts) > 0
    assert any(d.artifact_type == LearningArtifactType.ANTI_PATTERN for d in drafts)
    assert any(d.artifact_type == LearningArtifactType.CONSTRAINT_DISCOVERY for d in drafts)
    assert any(d.artifact_type == LearningArtifactType.DECISION_UPDATE for d in drafts)


def test_initiate_learn_sync(learn_service):
    """Test learn sync initiation."""
    proposal = learn_service.initiate_learn_sync(
        feature_name="test-feature",
        changed_files=["file1.py"],
        user_feedback="- Implemented successfully\n- Found constraint X"
    )
    
    assert proposal.proposal_id is not None
    assert proposal.feature_name == "test-feature"
    assert len(proposal.learning_drafts) >= 0
    assert proposal.changelog_entry is not None


def test_get_proposal(learn_service):
    """Test getting a proposal (with persistence)."""
    proposal = learn_service.initiate_learn_sync(
        feature_name="test-feature",
        changed_files=["file1.py"]
    )
    
    retrieved = learn_service.get_proposal(proposal.proposal_id)
    assert retrieved is not None
    assert retrieved.proposal_id == proposal.proposal_id


def test_list_proposals(learn_service):
    """Test listing proposals."""
    # Create a few proposals
    learn_service.initiate_learn_sync(
        feature_name="feature-1",
        changed_files=["file1.py"]
    )
    learn_service.initiate_learn_sync(
        feature_name="feature-2",
        changed_files=["file2.py"]
    )
    
    proposals = learn_service.list_proposals()
    assert len(proposals) >= 2
