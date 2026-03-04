"""Repository scanner for brownfield analysis.

Scans repository structure and detects languages, frameworks, entry points, and build tools.
"""

import os
from pathlib import Path
from typing import Optional

from ...domain.models.analysis import StructuralAnalysis
from ...shared.utils import find_repo_root


class RepositoryScanner:
    """Scans repository structure and analyzes it."""
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "python": [".py", "requirements.txt", "setup.py", "pyproject.toml"],
        "javascript": [".js", ".mjs", "package.json"],
        "typescript": [".ts", ".tsx", "tsconfig.json"],
        "go": [".go", "go.mod"],
        "rust": [".rs", "Cargo.toml"],
        "java": [".java", "pom.xml", "build.gradle"],
    }
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "react": ["package.json"],  # Check for react in dependencies
        "nextjs": ["next.config.js", "next.config.ts"],
        "django": ["manage.py", "settings.py"],
        "fastapi": ["main.py"],  # Common FastAPI entry point
        "express": ["package.json"],  # Check for express
    }
    
    # Entry point patterns
    ENTRY_POINT_PATTERNS = [
        "main.py", "app.py", "index.py",
        "index.js", "index.ts", "main.js", "main.ts",
        "main.go", "main.rs",
        "server.js", "server.ts",
    ]
    
    # Build tool patterns
    BUILD_TOOL_PATTERNS = {
        "make": ["Makefile"],
        "cmake": ["CMakeLists.txt"],
        "maven": ["pom.xml"],
        "gradle": ["build.gradle"],
        "npm": ["package.json"],
        "cargo": ["Cargo.toml"],
        "pip": ["requirements.txt", "setup.py"],
    }
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize scanner.
        
        Args:
            repo_root: Repository root path. Auto-detects if None.
        """
        if repo_root is None:
            repo_root = find_repo_root() or Path.cwd()
        self.repo_root = Path(repo_root).resolve()
    
    def scan(self) -> StructuralAnalysis:
        """Scan repository and perform structural analysis.
        
        Returns:
            StructuralAnalysis with repository structure information.
        """
        analysis = StructuralAnalysis(repo_root=str(self.repo_root))
        
        # Scan directory structure
        self._scan_structure(analysis)
        
        # Detect languages
        self._detect_languages(analysis)
        
        # Detect frameworks
        self._detect_frameworks(analysis)
        
        # Find entry points
        self._find_entry_points(analysis)
        
        # Detect build tools
        self._detect_build_tools(analysis)
        
        # Check for tests
        analysis.test_presence = self._has_tests()
        
        return analysis
    
    def _scan_structure(self, analysis: StructuralAnalysis):
        """Scan directory structure."""
        structure = {}
        file_count = 0
        total_size = 0
        
        # Exclude common directories
        exclude_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "dist", "build"}
        
        for root, dirs, files in os.walk(self.repo_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            rel_root = os.path.relpath(root, self.repo_root)
            if rel_root == ".":
                rel_root = "/"
            
            structure[rel_root] = {
                "files": [f for f in files if not f.startswith(".")],
                "subdirs": dirs,
            }
            
            for file in files:
                if not file.startswith("."):
                    file_path = Path(root) / file
                    if file_path.is_file():
                        file_count += 1
                        try:
                            total_size += file_path.stat().st_size
                        except OSError:
                            pass
        
        analysis.directory_structure = structure
        analysis.file_count = file_count
        analysis.total_size = total_size
    
    def _detect_languages(self, analysis: StructuralAnalysis):
        """Detect programming languages used."""
        languages = set()
        
        # Check file extensions
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            if any(excluded in root for excluded in [".git", "node_modules", "__pycache__"]):
                continue
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                for lang, patterns in self.LANGUAGE_PATTERNS.items():
                    if ext in patterns or file_path.name in patterns:
                        languages.add(lang)
        
        analysis.languages = languages
    
    def _detect_frameworks(self, analysis: StructuralAnalysis):
        """Detect frameworks used."""
        frameworks = set()
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            if any(excluded in root for excluded in [".git", "node_modules"]):
                continue
            
            for file in files:
                file_path = Path(root) / file
                
                # Check framework-specific files
                for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                    if file_path.name in patterns:
                        frameworks.add(framework)
                
                # Check package.json for frameworks
                if file_path.name == "package.json":
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        if "react" in content.lower():
                            frameworks.add("react")
                        if "express" in content.lower():
                            frameworks.add("express")
                        if "next" in content.lower():
                            frameworks.add("nextjs")
                    except Exception:
                        pass
        
        analysis.frameworks = frameworks
    
    def _find_entry_points(self, analysis: StructuralAnalysis):
        """Find entry point files."""
        entry_points = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            if any(excluded in root for excluded in [".git", "node_modules"]):
                continue
            
            for file in files:
                if file in self.ENTRY_POINT_PATTERNS:
                    file_path = Path(root) / file
                    rel_path = os.path.relpath(file_path, self.repo_root)
                    entry_points.append(rel_path)
        
        analysis.entry_points = sorted(set(entry_points))
    
    def _detect_build_tools(self, analysis: StructuralAnalysis):
        """Detect build tools used."""
        build_tools = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            if ".git" in root:
                continue
            
            for file in files:
                file_path = Path(root) / file
                
                for tool, patterns in self.BUILD_TOOL_PATTERNS.items():
                    if file_path.name in patterns:
                        build_tools.append(tool)
        
        analysis.build_tools = sorted(set(build_tools))
    
    def _has_tests(self) -> bool:
        """Check if repository has tests."""
        test_indicators = ["test", "tests", "__tests__", "spec", "specs"]
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            if any(excluded in root for excluded in [".git", "node_modules"]):
                continue
            
            # Check directory names
            for dir_name in dirs:
                if any(indicator in dir_name.lower() for indicator in test_indicators):
                    return True
            
            # Check file names
            for file in files:
                if any(indicator in file.lower() for indicator in test_indicators):
                    return True
        
        return False
