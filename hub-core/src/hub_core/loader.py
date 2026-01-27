"""Repository context loader for Context Mesh artifacts."""

import os
from pathlib import Path
from typing import Dict, Optional, Set
import re


class ContextLoader:
    """Loads and indexes Context Mesh artifacts from a repository."""
    
    # Allowed subdirectories under context/
    ALLOWED_SUBDIRS = {
        "intent",
        "decisions",
        "knowledge",
        "agents",
        "evolution",
    }
    
    # Allowed knowledge subdirectories
    ALLOWED_KNOWLEDGE_SUBDIRS = {
        "patterns",
        "anti-patterns",
    }
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize loader with repository root.
        
        Args:
            repo_root: Repository root path. If None, auto-detects.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.context_dir = self.repo_root / "context"
        self._index: Dict[str, Dict] = {
            "project_intent": None,
            "feature_intents": {},
            "decisions": {},
            "knowledge": {"patterns": {}, "anti-patterns": {}},
            "agents": {},
            "changelog": None,
        }
        self._loaded = False
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git or context/ directory.
        
        Returns:
            Path to repository root.
            
        Raises:
            ValueError: If repository root cannot be found.
        """
        current = Path.cwd().resolve()
        
        # Check current directory and parents
        for path in [current] + list(current.parents):
            if (path / ".git").exists() or (path / "context").exists():
                return path
        
        raise ValueError(
            "Could not find repository root. "
            "Expected .git directory or context/ directory."
        )
    
    def load(self) -> Dict[str, Dict]:
        """Load and index all context artifacts.
        
        Returns:
            Index dictionary with all loaded artifacts.
            
        Raises:
            FileNotFoundError: If context/ directory doesn't exist.
        """
        if not self.context_dir.exists():
            raise FileNotFoundError(
                f"Context directory not found: {self.context_dir}. "
                "Repository may not be Context Mesh compliant."
            )
        
        # Load project intent
        project_intent_path = self.context_dir / "intent" / "project-intent.md"
        if project_intent_path.exists():
            self._index["project_intent"] = {
                "path": str(project_intent_path.relative_to(self.repo_root)),
                "content": project_intent_path.read_text(encoding="utf-8"),
            }
        
        # Load feature intents
        intent_dir = self.context_dir / "intent"
        if intent_dir.exists():
            for file_path in intent_dir.glob("feature-*.md"):
                feature_name = file_path.stem.replace("feature-", "")
                self._index["feature_intents"][feature_name] = {
                    "path": str(file_path.relative_to(self.repo_root)),
                    "content": file_path.read_text(encoding="utf-8"),
                }
        
        # Load decisions
        decisions_dir = self.context_dir / "decisions"
        if decisions_dir.exists():
            for file_path in decisions_dir.glob("*.md"):
                # Extract decision number from filename (e.g., "001-tech-stack.md" -> "001")
                match = re.match(r"^(\d{3})-", file_path.name)
                if match:
                    decision_num = match.group(1)
                    self._index["decisions"][decision_num] = {
                        "path": str(file_path.relative_to(self.repo_root)),
                        "content": file_path.read_text(encoding="utf-8"),
                        "filename": file_path.name,
                    }
        
        # Load knowledge (patterns and anti-patterns)
        knowledge_dir = self.context_dir / "knowledge"
        if knowledge_dir.exists():
            for subdir_name in self.ALLOWED_KNOWLEDGE_SUBDIRS:
                subdir = knowledge_dir / subdir_name
                if subdir.exists():
                    for file_path in subdir.glob("*.md"):
                        if file_path.name != "README.md":  # Skip README files
                            name = file_path.stem
                            self._index["knowledge"][subdir_name][name] = {
                                "path": str(file_path.relative_to(self.repo_root)),
                                "content": file_path.read_text(encoding="utf-8"),
                            }
        
        # Load agents
        agents_dir = self.context_dir / "agents"
        if agents_dir.exists():
            for file_path in agents_dir.glob("agent-*.md"):
                agent_name = file_path.stem.replace("agent-", "")
                self._index["agents"][agent_name] = {
                    "path": str(file_path.relative_to(self.repo_root)),
                    "content": file_path.read_text(encoding="utf-8"),
                }
        
        # Load changelog
        changelog_path = self.context_dir / "evolution" / "changelog.md"
        if changelog_path.exists():
            self._index["changelog"] = {
                "path": str(changelog_path.relative_to(self.repo_root)),
                "content": changelog_path.read_text(encoding="utf-8"),
            }
        
        self._loaded = True
        return self._index
    
    def read_artifact(self, relative_path: str) -> str:
        """Safely read a context artifact file.
        
        Args:
            relative_path: Path relative to repository root (e.g., "context/intent/project-intent.md").
            
        Returns:
            File content as string.
            
        Raises:
            ValueError: If path is outside allowed context/ directory.
            FileNotFoundError: If file doesn't exist.
        """
        # Normalize path
        path = Path(relative_path)
        if path.is_absolute():
            path = Path(os.path.relpath(path, self.repo_root))
        
        # Resolve to absolute path
        full_path = (self.repo_root / path).resolve()
        
        # Security: Ensure path is within context/ directory
        context_abs = self.context_dir.resolve()
        try:
            full_path.relative_to(context_abs)
        except ValueError:
            raise ValueError(
                f"Path outside allowed context directory: {relative_path}. "
                "Only files under context/ are accessible."
            )
        
        # Check if file exists
        if not full_path.exists():
            raise FileNotFoundError(f"Context artifact not found: {relative_path}")
        
        return full_path.read_text(encoding="utf-8")
    
    @property
    def index(self) -> Dict[str, Dict]:
        """Get the context index.
        
        Returns:
            Index dictionary. Loads automatically if not already loaded.
        """
        if not self._loaded:
            self.load()
        return self._index
    
    def get_project_intent(self) -> Optional[Dict]:
        """Get project intent artifact."""
        return self.index.get("project_intent")
    
    def get_feature_intent(self, name: str) -> Optional[Dict]:
        """Get a feature intent by name."""
        return self.index["feature_intents"].get(name)
    
    def get_decision(self, number: str) -> Optional[Dict]:
        """Get a decision by number (e.g., "001")."""
        return self.index["decisions"].get(number)
    
    def list_features(self) -> Set[str]:
        """List all available feature intent names."""
        return set(self.index["feature_intents"].keys())
    
    def list_decisions(self) -> Set[str]:
        """List all available decision numbers."""
        return set(self.index["decisions"].keys())
