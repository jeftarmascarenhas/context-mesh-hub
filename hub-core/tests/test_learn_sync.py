"""Tests for Learn Sync functionality."""

import pytest
from pathlib import Path

from hub_core.learn_sync import (
    LearnSync,
    LearningArtifactType,
    ConfidenceLevel,
    ImpactLevel,
    OutcomeSummary,
)
from hub_core.loader import ContextLoader


def test_learn_sync_init():
    """Test Learn Sync initialization."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    learn_sync = LearnSync(loader)
    
    assert learn_sync.loader is not None
    assert learn_sync._proposals == {}


def test_collect_outcomes():
    """Test outcome collection."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    learn_sync = LearnSync(loader)
    
    outcome = learn_sync.collect_outcomes(
        feature_name="test-feature",
        changed_files=["file1.py", "file2.ts"],
        test_results="All tests passed",
        user_feedback="- Implemented feature X\n- Failed to implement feature Y"
    )
    
    assert len(outcome.what_implemented) > 0
    assert len(outcome.evidence_files) == 2
    assert "test-feature" in str(outcome)


def test_classify_learnings():
    """Test learning classification."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    learn_sync = LearnSync(loader)
    
    outcome = OutcomeSummary(
        what_failed=["Test failure in module X"],
        unexpected_difficulties=["Unexpected complexity in Y"],
        wrong_assumptions=["Assumed Z would work"],
        discovered_constraints=["Constraint A discovered"]
    )
    
    drafts = learn_sync.classify_learnings(outcome, "test-feature")
    
    assert len(drafts) > 0
    assert any(d.artifact_type == LearningArtifactType.ANTI_PATTERN for d in drafts)
    assert any(d.artifact_type == LearningArtifactType.CONSTRAINT_DISCOVERY for d in drafts)
    assert any(d.artifact_type == LearningArtifactType.DECISION_UPDATE for d in drafts)


def test_initiate_learn_sync():
    """Test learn sync initiation."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    learn_sync = LearnSync(loader)
    
    proposal = learn_sync.initiate_learn_sync(
        feature_name="test-feature",
        changed_files=["file1.py"],
        user_feedback="- Implemented successfully\n- Found constraint X"
    )
    
    assert proposal.proposal_id is not None
    assert proposal.feature_name == "test-feature"
    assert len(proposal.learning_drafts) >= 0
    assert proposal.changelog_entry is not None


def test_get_proposal():
    """Test getting a proposal."""
    repo_root = Path(__file__).parent.parent.parent
    loader = ContextLoader(repo_root)
    learn_sync = LearnSync(loader)
    
    proposal = learn_sync.initiate_learn_sync(
        feature_name="test-feature",
        changed_files=["file1.py"]
    )
    
    retrieved = learn_sync.get_proposal(proposal.proposal_id)
    assert retrieved is not None
    assert retrieved.proposal_id == proposal.proposal_id
    
    not_found = learn_sync.get_proposal("nonexistent-id")
    assert not_found is None
