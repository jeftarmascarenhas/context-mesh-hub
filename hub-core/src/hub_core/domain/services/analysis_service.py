"""Analysis Service - Brownfield analysis orchestration.

Pure business logic orchestrating infrastructure scanner modules.
Handles scan/slice/extract/report workflow for brownfield codebases.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from ...infrastructure.scanner.repo_scanner import RepositoryScanner
from ...infrastructure.scanner.slice_generator import SliceGenerator
from ...infrastructure.scanner.context_extractor import ContextExtractor
from ..models.analysis import (
    StructuralAnalysis,
    SliceDefinition,
    ProposedArtifact,
    Evidence,
)
from ...shared.errors import ValidationError, InvalidOperationError


class AnalysisService:
    """Service for brownfield repository analysis.
    
    Orchestrates:
    - Repository scanning (language/framework detection)
    - Slice generation (directory/module/language strategies)
    - Context extraction (4-layer artifact extraction)
    - Analysis reporting (comprehensive insights)
    """
    
    def __init__(
        self,
        scanner: RepositoryScanner,
        slice_generator: SliceGenerator,
        context_extractor: ContextExtractor,
    ):
        """Initialize analysis service with dependencies.
        
        Args:
            scanner: RepositoryScanner for structural analysis
            slice_generator: SliceGenerator for slicing strategies
            context_extractor: ContextExtractor for artifact extraction
        """
        self.scanner = scanner
        self.slice_generator = slice_generator
        self.context_extractor = context_extractor
        self._last_analysis: Optional[StructuralAnalysis] = None
        self._slices: Dict[str, SliceDefinition] = {}
    
    # ========================================================================
    # SCAN OPERATIONS
    # ========================================================================
    
    def scan(self, target_path: Optional[Path] = None) -> StructuralAnalysis:
        """Scan repository structure and detect technologies.
        
        Args:
            target_path: Optional path to scan (defaults to repo root)
        
        Returns:
            StructuralAnalysis with languages, frameworks, entry points, etc.
        """
        analysis = self.scanner.scan(target_path)
        self._last_analysis = analysis
        return analysis
    
    def get_last_analysis(self) -> Optional[StructuralAnalysis]:
        """Get the last performed structural analysis.
        
        Returns:
            StructuralAnalysis or None if no scan performed yet
        """
        return self._last_analysis
    
    # ========================================================================
    # SLICE OPERATIONS
    # ========================================================================
    
    def generate_slices(
        self,
        strategy: str,
        analysis: Optional[StructuralAnalysis] = None,
    ) -> List[SliceDefinition]:
        """Generate repository slices using specified strategy.
        
        Args:
            strategy: Slicing strategy ("directory", "module", "language")
            analysis: Optional StructuralAnalysis (uses last if not provided)
        
        Returns:
            List of SliceDefinition instances
            
        Raises:
            ValidationError: If invalid strategy
            InvalidOperationError: If no analysis available
        """
        # Validate strategy
        valid_strategies = ["directory", "module", "language"]
        if strategy not in valid_strategies:
            raise ValidationError(
                f"Invalid strategy: {strategy}",
                details={"valid_strategies": valid_strategies}
            )
        
        # Get analysis
        if analysis is None:
            analysis = self._last_analysis
        if analysis is None:
            raise InvalidOperationError(
                "No structural analysis available. Run scan() first.",
                details={"required_action": "scan"}
            )
        
        # Generate slices
        slices = self.slice_generator.generate_slices(strategy, analysis)
        
        # Store slices for later use
        for slice_def in slices:
            self._slices[slice_def.slice_id] = slice_def
        
        return slices
    
    def get_slice(self, slice_id: str) -> Optional[SliceDefinition]:
        """Get a slice by ID.
        
        Args:
            slice_id: Slice ID
        
        Returns:
            SliceDefinition or None if not found
        """
        return self._slices.get(slice_id)
    
    def list_slices(self) -> List[SliceDefinition]:
        """List all generated slices.
        
        Returns:
            List of SliceDefinition instances
        """
        return list(self._slices.values())
    
    # ========================================================================
    # EXTRACT OPERATIONS
    # ========================================================================
    
    def extract_artifacts(
        self,
        slice_id: str,
        analysis: Optional[StructuralAnalysis] = None,
    ) -> List[ProposedArtifact]:
        """Extract context artifacts from a slice.
        
        Uses 4-layer extraction:
        1. Structural Discovery (what exists)
        2. Intent Reconstruction (features)
        3. Decision Inference (technical choices)
        4. Risk Detection (concerns)
        
        Args:
            slice_id: Slice ID to extract from
            analysis: Optional StructuralAnalysis (uses last if not provided)
        
        Returns:
            List of ProposedArtifact instances
            
        Raises:
            InvalidOperationError: If slice not found or no analysis available
        """
        # Get slice
        slice_def = self.get_slice(slice_id)
        if not slice_def:
            raise InvalidOperationError(
                f"Slice not found: {slice_id}. Generate slices first.",
                details={"available_slices": list(self._slices.keys())}
            )
        
        # Get analysis
        if analysis is None:
            analysis = self._last_analysis
        if analysis is None:
            raise InvalidOperationError(
                "No structural analysis available. Run scan() first.",
                details={"required_action": "scan"}
            )
        
        # Extract artifacts
        artifacts = self.context_extractor.extract_from_slice(slice_def, analysis)
        
        return artifacts
    
    def extract_all_slices(
        self,
        analysis: Optional[StructuralAnalysis] = None,
    ) -> Dict[str, List[ProposedArtifact]]:
        """Extract artifacts from all generated slices.
        
        Args:
            analysis: Optional StructuralAnalysis (uses last if not provided)
        
        Returns:
            Dict mapping slice_id to list of ProposedArtifact
            
        Raises:
            InvalidOperationError: If no slices available
        """
        if not self._slices:
            raise InvalidOperationError(
                "No slices available. Generate slices first.",
                details={"required_action": "generate_slices"}
            )
        
        results = {}
        for slice_id in self._slices:
            results[slice_id] = self.extract_artifacts(slice_id, analysis)
        
        return results
    
    # ========================================================================
    # REPORT OPERATIONS
    # ========================================================================
    
    def generate_report(
        self,
        slice_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis report.
        
        Args:
            slice_filter: Optional slice ID to filter report
        
        Returns:
            Dict with report data
            
        Raises:
            InvalidOperationError: If no analysis available
        """
        if not self._last_analysis:
            raise InvalidOperationError(
                "No analysis available. Run scan() first.",
                details={"required_action": "scan"}
            )
        
        report = {
            "analysis": {
                "languages": self._last_analysis.languages,
                "frameworks": self._last_analysis.frameworks,
                "build_tools": self._last_analysis.build_tools,
                "entry_points": self._last_analysis.entry_points,
                "has_tests": self._last_analysis.has_tests,
                "file_count": self._last_analysis.file_count,
                "directory_count": self._last_analysis.directory_count,
            },
            "slices": {
                "total": len(self._slices),
                "strategies_used": list(set(s.strategy for s in self._slices.values())),
            },
            "artifacts": {
                "total": 0,
                "by_type": {},
                "by_slice": {},
            },
        }
        
        # Add slice details
        if slice_filter:
            slices_to_report = [self._slices.get(slice_filter)] if slice_filter in self._slices else []
        else:
            slices_to_report = list(self._slices.values())
        
        report["slices"]["items"] = [
            {
                "slice_id": s.slice_id,
                "name": s.name,
                "strategy": s.strategy,
                "path": str(s.path),
                "file_count": len(s.file_paths),
            }
            for s in slices_to_report
        ]
        
        # Aggregate artifact stats (if extracted)
        for slice_def in slices_to_report:
            # Note: Artifacts are extracted on-demand, not stored
            # This is a summary report, actual extraction happens separately
            pass
        
        return report
    
    # ========================================================================
    # IMPACT OPERATIONS
    # ========================================================================
    
    def analyze_impact(
        self,
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """Analyze impact of file changes on slices and artifacts.
        
        Args:
            changed_files: List of changed file paths
        
        Returns:
            Dict with impact analysis
        """
        impact = {
            "changed_files": changed_files,
            "affected_slices": [],
            "potentially_affected_artifacts": [],
        }
        
        # Find affected slices
        for slice_def in self._slices.values():
            for changed_file in changed_files:
                if any(changed_file.startswith(str(fp)) for fp in slice_def.file_paths):
                    impact["affected_slices"].append({
                        "slice_id": slice_def.slice_id,
                        "name": slice_def.name,
                        "strategy": slice_def.strategy,
                    })
                    break
        
        return impact
    
    # ========================================================================
    # DEPENDENCY OPERATIONS
    # ========================================================================
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies from structural analysis.
        
        Returns:
            Dict with dependency analysis
            
        Raises:
            InvalidOperationError: If no analysis available
        """
        if not self._last_analysis:
            raise InvalidOperationError(
                "No analysis available. Run scan() first.",
                details={"required_action": "scan"}
            )
        
        dependencies = {
            "build_tools": self._last_analysis.build_tools,
            "frameworks": self._last_analysis.frameworks,
            "languages": self._last_analysis.languages,
            "inferred_dependencies": [],
        }
        
        # Infer common dependencies based on frameworks
        for framework in self._last_analysis.frameworks:
            if framework == "FastAPI":
                dependencies["inferred_dependencies"].extend(["fastapi", "uvicorn", "pydantic"])
            elif framework == "Flask":
                dependencies["inferred_dependencies"].append("flask")
            elif framework == "Django":
                dependencies["inferred_dependencies"].append("django")
            elif framework == "React":
                dependencies["inferred_dependencies"].extend(["react", "react-dom"])
            elif framework == "Next.js":
                dependencies["inferred_dependencies"].extend(["next", "react", "react-dom"])
        
        # Deduplicate
        dependencies["inferred_dependencies"] = list(set(dependencies["inferred_dependencies"]))
        
        return dependencies
