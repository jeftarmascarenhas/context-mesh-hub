"""Slice generator for repository analysis.

Divides repository into analyzable slices using different strategies.
"""

import os
from pathlib import Path
from typing import Dict, List

from ...domain.models.analysis import SliceDefinition
from .repo_scanner import RepositoryScanner


class SliceGenerator:
    """Generates repository slices for analysis."""
    
    def __init__(self, scanner: RepositoryScanner):
        """Initialize slice generator.
        
        Args:
            scanner: RepositoryScanner instance.
        """
        self.scanner = scanner
        self.repo_root = scanner.repo_root
    
    def generate_slices(self, strategy: str = "directory") -> List[SliceDefinition]:
        """Generate slices from repository.
        
        Args:
            strategy: Slice strategy ("directory", "module", "language").
        
        Returns:
            List of SliceDefinition instances.
            
        Raises:
            ValueError: If strategy is unknown.
        """
        if strategy == "directory":
            return self._generate_directory_slices()
        elif strategy == "module":
            return self._generate_module_slices()
        elif strategy == "language":
            return self._generate_language_slices()
        else:
            raise ValueError(f"Unknown slice strategy: {strategy}")
    
    def _generate_directory_slices(self) -> List[SliceDefinition]:
        """Generate slices based on top-level directories."""
        slices = []
        slice_num = 1
        
        # Get top-level directories
        top_level_dirs = [
            d for d in self.repo_root.iterdir()
            if d.is_dir() and not d.name.startswith(".") and d.name not in ["node_modules", "__pycache__"]
        ]
        
        for dir_path in sorted(top_level_dirs):
            slice_id = f"slice-{slice_num:03d}"
            name = dir_path.name
            
            # Count files in slice
            file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file() and not _.name.startswith("."))
            
            # Detect languages in slice
            languages = set()
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    for lang, patterns in RepositoryScanner.LANGUAGE_PATTERNS.items():
                        if ext in patterns or file_path.name in patterns:
                            languages.add(lang)
            
            slice_def = SliceDefinition(
                slice_id=slice_id,
                name=name,
                paths=[str(dir_path.relative_to(self.repo_root))],
                languages=languages,
                file_count=file_count,
            )
            slices.append(slice_def)
            slice_num += 1
        
        return slices
    
    def _generate_module_slices(self) -> List[SliceDefinition]:
        """Generate slices based on module/package boundaries.
        
        For now, falls back to directory-based slicing.
        Can be enhanced to detect actual package boundaries.
        """
        return self._generate_directory_slices()
    
    def _generate_language_slices(self) -> List[SliceDefinition]:
        """Generate slices based on programming languages."""
        slices = []
        language_dirs: Dict[str, List[str]] = {}
        
        # Group directories by primary language
        for root, dirs, files in os.walk(self.repo_root):
            if ".git" in root or "node_modules" in root:
                continue
            
            rel_root = os.path.relpath(root, self.repo_root)
            if rel_root == ".":
                rel_root = "/"
            
            # Determine primary language in this directory
            lang_counts: Dict[str, int] = {}
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                for lang, patterns in RepositoryScanner.LANGUAGE_PATTERNS.items():
                    if ext in patterns or file_path.name in patterns:
                        lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
            if lang_counts:
                primary_lang = max(lang_counts, key=lang_counts.get)
                if primary_lang not in language_dirs:
                    language_dirs[primary_lang] = []
                language_dirs[primary_lang].append(rel_root)
        
        # Create slices for each language
        slice_num = 1
        for lang, dirs in language_dirs.items():
            slice_id = f"slice-{slice_num:03d}"
            slice_def = SliceDefinition(
                slice_id=slice_id,
                name=f"{lang}-code",
                paths=dirs,
                languages={lang},
                file_count=0,  # Would need to count
            )
            slices.append(slice_def)
            slice_num += 1
        
        return slices
