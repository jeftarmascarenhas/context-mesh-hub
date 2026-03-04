"""Context extractor for brownfield analysis.

Extracts proposed context artifacts from repository slices using a layered approach.
"""

import os
from pathlib import Path
from typing import List

from ...domain.models.analysis import (
    SliceDefinition,
    ProposedArtifact,
    Evidence,
    ConfidenceLevel,
)
from .repo_scanner import RepositoryScanner


class ContextExtractor:
    """Extracts proposed context artifacts from repository slices.
    
    Uses a 4-layer extraction strategy per Decision D005:
    1. Structural Discovery - Architecture decisions from structure
    2. Intent Reconstruction - Features from high-level indicators
    3. Decision Inference - Technical choices from patterns
    4. Risk Detection - Potential issues and fragility
    
    Per Decision D014: Features represent value, Decisions represent technical choices.
    Entry points are implementation details → documented as Decisions, not Features.
    """
    
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
        """Layer 1: Extract structural discovery artifacts.
        
        Per Decision D014: Structural analysis should identify Decisions
        (tech stack, architecture) rather than Features.
        """
        artifacts = []
        
        # Create a structural summary as a Decision about architecture
        content = f"""# PROPOSED: Decision - Architecture of {slice_def.name}

## Context
Structural analysis of repository slice: {slice_def.name}

## Structure Discovery
- Paths: {', '.join(slice_def.paths)}
- Languages: {', '.join(slice_def.languages) if slice_def.languages else 'Unknown'}
- File count: {slice_def.file_count}

## Evidence
- Slice ID: {slice_def.slice_id}
- Analyzed paths: {', '.join(slice_def.paths)}

## Confidence
SUSPECTED - Based on directory structure analysis

## Open Questions
- What architectural decisions led to this structure?
- Are there hidden dependencies not visible in structure?
- What is the responsibility of this module/component?
"""
        
        artifact = ProposedArtifact(
            artifact_type="decision",  # Changed from "feature_intent" to "decision"
            title=f"Architecture: {slice_def.name}",
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
                "What architectural decisions led to this structure?",
                "Are there hidden dependencies?",
                "What is the responsibility of this component?",
            ],
        )
        artifacts.append(artifact)
        
        return artifacts
    
    def _extract_intent_reconstruction(self, slice_def: SliceDefinition) -> List[ProposedArtifact]:
        """Layer 2: Extract intent reconstruction artifacts.
        
        Per Decision D014: Features represent value to users/system, NOT technical files.
        Entry points (main.py, server.py) should be documented as Decisions about
        architecture/entry points, not as Features.
        
        This layer should focus on identifying system capabilities from:
        - API route structures (what endpoints exist)
        - Directory naming that suggests features (auth/, payments/, etc.)
        - README files describing functionality
        """
        artifacts = []
        
        # Look for feature-indicating directory structures
        for path_str in slice_def.paths:
            path = self.repo_root / path_str
            if not path.exists():
                continue
            
            # Check for feature-indicating subdirectories
            feature_dirs = ["api", "routes", "endpoints", "features", "services"]
            for subdir_name in feature_dirs:
                subdir = path / subdir_name
                if subdir.exists() and subdir.is_dir():
                    # This suggests a feature-oriented architecture
                    # Could extract features from subdirectory names
                    pass
            
            # Check for README files that might describe features
            readme_files = list(path.glob("README.md")) + list(path.glob("README.txt"))
            for readme in readme_files:
                # README might describe features - could parse it
                pass
        
        # Note: Removed automatic "Feature Intent" generation for entry points
        # Per D014, entry points are implementation details, not features
        # Features should be extracted from higher-level indicators of value
        
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
