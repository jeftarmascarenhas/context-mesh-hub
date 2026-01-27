"""Basic tests for context loader."""

import pytest
from pathlib import Path
from hub_core.loader import ContextLoader


def test_find_repo_root():
    """Test repository root detection."""
    # This test assumes we're running from the hub-core directory
    # and the repo root is the parent
    loader = ContextLoader()
    assert loader.repo_root.exists()
    assert (loader.repo_root / "context").exists()


def test_load_context():
    """Test loading context artifacts."""
    loader = ContextLoader()
    index = loader.load()
    
    # Should have project intent
    assert index.get("project_intent") is not None
    
    # Should have some feature intents
    assert len(index["feature_intents"]) > 0
    
    # Should have decisions
    assert len(index["decisions"]) > 0


def test_read_artifact():
    """Test reading artifacts safely."""
    loader = ContextLoader()
    loader.load()
    
    # Should be able to read project intent
    project_intent = loader.get_project_intent()
    assert project_intent is not None
    
    content = loader.read_artifact(project_intent["path"])
    assert len(content) > 0


def test_path_safety():
    """Test that path safety prevents reading outside context/."""
    loader = ContextLoader()
    
    # Should raise ValueError for paths outside context/
    with pytest.raises(ValueError):
        loader.read_artifact("../../etc/passwd")
    
    with pytest.raises(ValueError):
        loader.read_artifact("/etc/passwd")
