"""Brownfield context extraction for existing repositories."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level for extracted context."""
    CONFIRMED = "confirmed"
    SUSPECTED = "suspected"
    UNKNOWN = "unknown"


@dataclass
class Evidence:
    """Evidence reference for a claim."""
    file_path: str
    line_range: Optional[tuple] = None  # (start_line, end_line)
    code_snippet: Optional[str] = None
    description: str = ""


@dataclass
class ProposedArtifact:
    """A proposed context artifact from brownfield extraction."""
    artifact_type: str  # "feature_intent", "decision", "pattern", "anti_pattern"
    title: str
    content: str  # Markdown content
    confidence: ConfidenceLevel
    evidence: List[Evidence] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    proposed_at: str = ""


@dataclass
class StructuralAnalysis:
    """Structural analysis of a repository."""
    repo_root: str
    languages: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    entry_points: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    test_presence: bool = False
    directory_structure: Dict = field(default_factory=dict)
    file_count: int = 0
    total_size: int = 0  # bytes


@dataclass
class SliceDefinition:
    """Definition of a repository slice."""
    slice_id: str
    name: str
    paths: List[str]  # Directory paths included in slice
    languages: Set[str] = field(default_factory=set)
    file_count: int = 0
    dependencies: List[str] = field(default_factory=list)  # Other slice IDs


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
            repo_root = self._find_repo_root()
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
    
    def _find_repo_root(self) -> Path:
        """Find repository root."""
        current = Path.cwd().resolve()
        for path in [current] + list(current.parents):
            if (path / ".git").exists() or (path / "context").exists():
                return path
        return current
    
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
        """Generate slices based on module/package boundaries."""
        # For now, fall back to directory-based
        # Can be enhanced to detect package boundaries
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


class ContextExtractor:
    """Extracts proposed context artifacts from repository slices."""
    
    def __init__(self, scanner: RepositoryScanner):
        """Initialize extractor.
        
        Args:
            scanner: RepositoryScanner instance.
        """
        self.scanner = scanner
        self.repo_root = scanner.repo_root
    
    def extract_from_slice(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Extract proposed context artifacts from a slice.
        
        Args:
            slice_def: SliceDefinition to extract from.
        
        Returns:
            List of ProposedArtifact instances.
        """
        artifacts = []
        
        # Layer 1: Structural Discovery
        structural_artifacts = self._extract_structural_discovery(slice_def)
        artifacts.extend(structural_artifacts)
        
        # Layer 2: Intent Reconstruction
        intent_artifacts = self._extract_intent_reconstruction(slice_def)
        artifacts.extend(intent_artifacts)
        
        # Layer 3: Decision Inference
        decision_artifacts = self._extract_decision_inference(slice_def)
        artifacts.extend(decision_artifacts)
        
        # Layer 4: Risk & Fragility Detection
        risk_artifacts = self._extract_risk_detection(slice_def)
        artifacts.extend(risk_artifacts)
        
        return artifacts
    
    def _extract_structural_discovery(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Layer 1: Extract structural discovery artifacts."""
        artifacts = []
        
        # Create a structural summary
        content = f"""# PROPOSED: Structural Analysis - {slice_def.name}

## What
Structural analysis of repository slice: {slice_def.name}

## Structure
- Paths: {', '.join(slice_def.paths)}
- Languages: {', '.join(slice_def.languages)}
- File count: {slice_def.file_count}

## Evidence
- Slice ID: {slice_def.slice_id}
- Analyzed paths: {', '.join(slice_def.paths)}

## Confidence
SUSPECTED - Based on directory structure analysis

## Open Questions
- What is the primary purpose of this slice?
- Are there hidden dependencies not visible in structure?
"""
        
        artifact = ProposedArtifact(
            artifact_type="feature_intent",
            title=f"Structural Analysis: {slice_def.name}",
            content=content,
            confidence=ConfidenceLevel.SUSPECTED,
            evidence=[
                Evidence(
                    file_path=path,
                    description=f"Directory in slice {slice_def.slice_id}"
                )
                for path in slice_def.paths
            ],
            open_questions=[
                "What is the primary purpose of this slice?",
                "Are there hidden dependencies?",
            ],
        )
        artifacts.append(artifact)
        
        return artifacts
    
    def _extract_intent_reconstruction(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Layer 2: Extract intent reconstruction artifacts."""
        artifacts = []
        
        # Infer intent from naming and structure
        # This is a simplified version - can be enhanced
        
        for path_str in slice_def.paths:
            path = self.repo_root / path_str
            if not path.exists():
                continue
            
            # Look for main files or entry points
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.name in RepositoryScanner.ENTRY_POINT_PATTERNS:
                    # Found potential entry point
                    content = f"""# PROPOSED: Feature Intent - {file_path.stem}

## What
Potential feature/module identified from entry point: {file_path.name}

## Why
Entry point file suggests this is a main component or feature.

## Evidence
- Entry point: {os.path.relpath(file_path, self.repo_root)}
- Slice: {slice_def.name}

## Confidence
SUSPECTED - Based on entry point detection

## Open Questions
- What is the actual purpose of this component?
- What are its dependencies?
- What are its responsibilities?
"""
                    
                    artifact = ProposedArtifact(
                        artifact_type="feature_intent",
                        title=f"Feature: {file_path.stem}",
                        content=content,
                        confidence=ConfidenceLevel.SUSPECTED,
                        evidence=[
                            Evidence(
                                file_path=os.path.relpath(file_path, self.repo_root),
                                description="Entry point file"
                            )
                        ],
                        open_questions=[
                            "What is the actual purpose?",
                            "What are dependencies?",
                        ],
                    )
                    artifacts.append(artifact)
        
        return artifacts
    
    def _extract_decision_inference(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Layer 3: Extract decision inference artifacts."""
        artifacts = []
        
        # Infer decisions from patterns
        # Simplified version - can be enhanced with deeper analysis
        
        if "python" in slice_def.languages:
            # Check for framework decisions
            for path_str in slice_def.paths:
                path = self.repo_root / path_str
                if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
                    content = f"""# PROPOSED: Decision - Python Dependency Management

## Context
Repository slice uses Python with dependency management files.

## Decision
Python dependencies are managed via requirements.txt or pyproject.toml.

## Evidence
- Dependency file found in: {path_str}
- Language: Python

## Confidence
CONFIRMED - Dependency file present

## Open Questions
- Why was this dependency management approach chosen?
- Are there constraints or requirements?
"""
                    
                    artifact = ProposedArtifact(
                        artifact_type="decision",
                        title="Python Dependency Management",
                        content=content,
                        confidence=ConfidenceLevel.CONFIRMED,
                        evidence=[
                            Evidence(
                                file_path=os.path.relpath(path / "requirements.txt" if (path / "requirements.txt").exists() else path / "pyproject.toml", self.repo_root),
                                description="Dependency management file"
                            )
                        ],
                    )
                    artifacts.append(artifact)
        
        return artifacts
    
    def _extract_risk_detection(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Layer 4: Extract risk and fragility detection artifacts."""
        artifacts = []
        
        # Detect potential risks
        # Simplified version - can be enhanced
        
        risks = []
        
        # Check for large files (potential complexity)
        for path_str in slice_def.paths:
            path = self.repo_root / path_str
            if not path.exists():
                continue
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        if size > 100000:  # 100KB
                            risks.append(f"Large file detected: {os.path.relpath(file_path, self.repo_root)} ({size} bytes)")
                    except OSError:
                        pass
        
        if risks:
            content = f"""# PROPOSED: Risk Annotation - {slice_def.name}

## Risk
Potential complexity or maintainability concerns in slice.

## Details
{chr(10).join('- ' + risk for risk in risks)}

## Evidence
- Slice: {slice_def.name}
- Risks identified: {len(risks)}

## Confidence
SUSPECTED - Based on file size analysis

## Open Questions
- Are large files justified?
- Is refactoring needed?
"""
            
            artifact = ProposedArtifact(
                artifact_type="risk",
                title=f"Risk: {slice_def.name}",
                content=content,
                confidence=ConfidenceLevel.SUSPECTED,
                evidence=[
                    Evidence(
                        file_path=path_str,
                        description="Slice with potential risks"
                    )
                    for path_str in slice_def.paths
                ],
                open_questions=[
                    "Are large files justified?",
                    "Is refactoring needed?",
                ],
            )
            artifacts.append(artifact)
        
        return artifacts
