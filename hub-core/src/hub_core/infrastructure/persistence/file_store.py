"""File-based storage for Context Mesh Hub.

Provides JSON-based persistence for plans and proposals while maintaining
repo-first approach (no database dependency).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...shared.errors import PersistenceError


class FileStore:
    """Generic file-based key-value store using JSON.
    
    Stores data in .context-mesh/ directory with JSON format for
    git-friendliness and easy inspection.
    
    Directory is created lazily on first write to avoid creating
    empty directories when MCP server starts.
    """
    
    def __init__(self, base_path: Path):
        """Initialize file store.
        
        Args:
            base_path: Base directory for storage (e.g., repo_root / ".context-mesh").
        """
        self.base_path = Path(base_path)
        # Note: Directory is created lazily in save() method
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save data to file.
        
        Args:
            key: Unique identifier (will be filename).
            data: Data to save (must be JSON-serializable).
            
        Raises:
            PersistenceError: If save fails.
        """
        file_path = self.base_path / f"{key}.json"
        
        try:
            # Create directory lazily on first write
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise PersistenceError(
                operation="save",
                path=str(file_path),
                reason=str(e)
            )
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data from file.
        
        Args:
            key: Unique identifier.
            
        Returns:
            Loaded data, or None if not found.
            
        Raises:
            PersistenceError: If load fails (but not if file doesn't exist).
        """
        file_path = self.base_path / f"{key}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise PersistenceError(
                operation="load",
                path=str(file_path),
                reason=str(e)
            )
    
    def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Unique identifier.
            
        Returns:
            True if file exists.
        """
        file_path = self.base_path / f"{key}.json"
        return file_path.exists()
    
    def delete(self, key: str) -> None:
        """Delete file.
        
        Args:
            key: Unique identifier.
            
        Raises:
            PersistenceError: If delete fails.
        """
        file_path = self.base_path / f"{key}.json"
        
        if not file_path.exists():
            return
        
        try:
            file_path.unlink()
        except Exception as e:
            raise PersistenceError(
                operation="delete",
                path=str(file_path),
                reason=str(e)
            )
    
    def list_keys(self) -> List[str]:
        """List all keys in store.
        
        Returns:
            List of keys (filenames without .json extension).
        """
        if not self.base_path.exists():
            return []
        
        return [
            f.stem
            for f in self.base_path.glob("*.json")
            if f.is_file()
        ]
