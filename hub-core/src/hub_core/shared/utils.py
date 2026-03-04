"""Utility functions for Context Mesh Hub Core."""

import re
from pathlib import Path
from typing import Optional


def slugify(text: str) -> str:
    """Convert text to slug format (lowercase, hyphens).
    
    Args:
        text: Text to slugify.
        
    Returns:
        Slugified text.
        
    Example:
        >>> slugify("User Authentication System")
        'user-authentication-system'
    """
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def extract_number_from_id(identifier: str) -> Optional[int]:
    """Extract numeric ID from artifact identifier.
    
    Args:
        identifier: Artifact ID (e.g., "F001", "D042", "001").
        
    Returns:
        Numeric part as integer, or None if not found.
        
    Example:
        >>> extract_number_from_id("F001")
        1
        >>> extract_number_from_id("D042")
        42
    """
    match = re.search(r'\d+', identifier)
    return int(match.group()) if match else None


def format_artifact_id(prefix: str, number: int, padding: int = 3) -> str:
    """Format artifact ID with prefix and zero-padded number.
    
    Args:
        prefix: Prefix letter (F, D, etc.).
        number: Numeric ID.
        padding: Number of digits (default 3).
        
    Returns:
        Formatted ID.
        
    Example:
        >>> format_artifact_id("F", 1)
        'F001'
        >>> format_artifact_id("D", 42)
        'D042'
    """
    return f"{prefix}{number:0{padding}d}"


def find_repo_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find repository root by looking for .git or context/ directory.
    
    Args:
        start_path: Starting path (defaults to current directory).
        
    Returns:
        Repository root path, or None if not found.
    """
    current = (start_path or Path.cwd()).resolve()
    
    for path in [current] + list(current.parents):
        if (path / ".git").exists() or (path / "context").exists():
            return path
    
    return None


def is_excluded_path(path: Path, excluded_dirs: set, excluded_files: set) -> bool:
    """Check if path should be excluded from scanning.
    
    Args:
        path: Path to check.
        excluded_dirs: Set of directory names to exclude.
        excluded_files: Set of file patterns to exclude.
        
    Returns:
        True if path should be excluded.
    """
    # Check if any parent directory is excluded
    for part in path.parts:
        if part in excluded_dirs:
            return True
    
    # Check if filename matches excluded patterns
    if path.is_file():
        name = path.name
        for pattern in excluded_files:
            if '*' in pattern:
                # Simple glob matching
                pattern_re = pattern.replace('.', r'\.').replace('*', '.*')
                if re.match(pattern_re, name):
                    return True
            elif name == pattern:
                return True
    
    return False
