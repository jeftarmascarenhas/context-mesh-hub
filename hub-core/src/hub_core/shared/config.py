"""Configuration management for Context Mesh Hub Core."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Global configuration for Hub Core.
    
    Centralizes paths, constants, and environment-based settings.
    """
    
    # Directory names
    CONTEXT_DIR = "context"
    INTENT_DIR = "intent"
    DECISIONS_DIR = "decisions"
    KNOWLEDGE_DIR = "knowledge"
    PATTERNS_DIR = "patterns"
    ANTI_PATTERNS_DIR = "anti-patterns"
    AGENTS_DIR = "agents"
    EVOLUTION_DIR = "evolution"
    
    # File names
    PROJECT_INTENT_FILE = "project-intent.md"
    CHANGELOG_FILE = "changelog.md"
    AGENTS_FILE = "AGENTS.md"
    
    # Persistence
    PERSISTENCE_DIR = ".context-mesh"
    PLANS_DIR = "plans"
    PROPOSALS_DIR = "proposals"
    TEMP_DIR = "temp"
    
    # Naming patterns
    FEATURE_PATTERN = r"^F\d{3,}-.*\.md$"
    DECISION_PATTERN = r"^D\d{3,}-.*\.md$"
    BUG_PATTERN = r"^bug-.*\.md$"
    AGENT_PATTERN = r"^agent-.*\.md$"
    
    # Exclusions for scanning
    EXCLUDED_DIRS = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "target", "dist", "build", ".pytest_cache", ".mypy_cache",
        ".tox", "htmlcov", ".coverage", "*.egg-info"
    }
    
    EXCLUDED_FILES = {
        ".DS_Store", "Thumbs.db", "*.pyc", "*.pyo", "*.swp",
        "*.swo", "*.swn", ".gitignore", ".gitkeep"
    }
    
    @classmethod
    def get_context_dir(cls, repo_root: Path) -> Path:
        """Get context directory path."""
        return repo_root / cls.CONTEXT_DIR
    
    @classmethod
    def get_persistence_dir(cls, repo_root: Path) -> Path:
        """Get persistence directory path."""
        return repo_root / cls.PERSISTENCE_DIR
    
    @classmethod
    def get_plans_dir(cls, repo_root: Path) -> Path:
        """Get plans directory path."""
        return cls.get_persistence_dir(repo_root) / cls.PLANS_DIR
    
    @classmethod
    def get_proposals_dir(cls, repo_root: Path) -> Path:
        """Get proposals directory path."""
        return cls.get_persistence_dir(repo_root) / cls.PROPOSALS_DIR
    
    @classmethod
    def ensure_persistence_dirs(cls, repo_root: Path) -> None:
        """Ensure persistence directories exist."""
        plans_dir = cls.get_plans_dir(repo_root)
        proposals_dir = cls.get_proposals_dir(repo_root)
        
        plans_dir.mkdir(parents=True, exist_ok=True)
        proposals_dir.mkdir(parents=True, exist_ok=True)
        
        # Add .gitignore to exclude temp files
        gitignore_path = cls.get_persistence_dir(repo_root) / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("temp/\n*.tmp\n")
    
    @classmethod
    def from_env(cls) -> Optional[Path]:
        """Get repo root from environment variable."""
        env_root = os.environ.get("CONTEXT_MESH_REPO_ROOT")
        return Path(env_root).resolve() if env_root else None
