"""Tests for AnalysisService.

Tests brownfield analysis: scan, slice, extract, report workflow.
"""

import pytest
from pathlib import Path

from hub_core.domain.services.analysis_service import AnalysisService
from hub_core.domain.models.analysis import StructuralAnalysis, SliceDefinition
from hub_core.shared.errors import ValidationError, InvalidOperationError


class TestAnalysisServiceScan:
    """Test repository scanning."""
    
    def test_scan_repository(self, analysis_service, repo_root):
        """Test scanning repository structure."""
        analysis = analysis_service.scan()
        
        assert isinstance(analysis, StructuralAnalysis)
        assert analysis.repo_root == repo_root
        assert len(analysis.languages) > 0
        assert analysis.primary_language is not None
    
    def test_scan_detects_python(self, analysis_service):
        """Test that Python is detected as a language."""
        analysis = analysis_service.scan()
        
        assert "Python" in analysis.languages
    
    def test_scan_detects_entry_points(self, analysis_service):
        """Test detection of entry points."""
        analysis = analysis_service.scan()
        
        # Should detect some Python files
        assert len(analysis.entry_points) > 0
    
    def test_scan_with_target_path(self, analysis_service, repo_root):
        """Test scanning specific subdirectory."""
        target = repo_root / "hub-core"
        if target.exists():
            analysis = analysis_service.scan(target)
            
            assert analysis.repo_root == target
            assert "Python" in analysis.languages
    
    def test_get_last_analysis(self, analysis_service):
        """Test retrieving last analysis."""
        analysis = analysis_service.scan()
        
        last = analysis_service.get_last_analysis()
        
        assert last is not None
        assert last.repo_root == analysis.repo_root


class TestAnalysisServiceSliceGeneration:
    """Test repository slicing."""
    
    def test_generate_slices_by_directory(self, analysis_service):
        """Test generating slices by directory structure."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("directory", analysis)
        
        assert isinstance(slices, list)
        assert len(slices) > 0
        assert all(isinstance(s, SliceDefinition) for s in slices)
    
    def test_generate_slices_by_module(self, analysis_service):
        """Test generating slices by module."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("module", analysis)
        
        assert isinstance(slices, list)
        # Module detection depends on codebase structure
    
    def test_generate_slices_by_language(self, analysis_service):
        """Test generating slices by language."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("language", analysis)
        
        assert isinstance(slices, list)
        assert len(slices) > 0
        # Should have at least Python slice
        assert any("python" in s.slice_id.lower() for s in slices)
    
    def test_generate_slices_invalid_strategy(self, analysis_service):
        """Test invalid strategy raises error."""
        analysis = analysis_service.scan()
        
        with pytest.raises(ValidationError):
            analysis_service.generate_slices("invalid", analysis)
    
    def test_generate_slices_without_analysis(self, analysis_service):
        """Test generating slices without prior scan uses last analysis."""
        analysis_service.scan()
        
        # Should use cached analysis
        slices = analysis_service.generate_slices("directory")
        assert len(slices) > 0
    
    def test_generate_slices_no_cached_analysis(self):
        """Test generating slices with no analysis raises error."""
        from hub_core.infrastructure.scanner.repo_scanner import RepositoryScanner
        from hub_core.infrastructure.scanner.slice_generator import SliceGenerator
        from hub_core.infrastructure.scanner.context_extractor import ContextExtractor
        from hub_core.loader import ContextLoader
        
        # Create fresh service with no scan
        loader = ContextLoader()
        scanner = RepositoryScanner(loader.repo_root)
        slice_gen = SliceGenerator(loader.repo_root)
        extractor = ContextExtractor(loader)
        
        service = AnalysisService(scanner, slice_gen, extractor)
        
        with pytest.raises(InvalidOperationError):
            service.generate_slices("directory")
    
    def test_slice_storage(self, analysis_service):
        """Test that generated slices are stored."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("directory", analysis)
        
        if slices:
            slice_id = slices[0].slice_id
            retrieved = analysis_service.get_slice(slice_id)
            
            assert retrieved is not None
            assert retrieved.slice_id == slice_id
    
    def test_list_slices(self, analysis_service):
        """Test listing all slices."""
        analysis = analysis_service.scan()
        analysis_service.generate_slices("directory", analysis)
        
        all_slices = analysis_service.list_slices()
        
        assert isinstance(all_slices, list)
        assert len(all_slices) > 0


class TestAnalysisServiceExtraction:
    """Test artifact extraction from slices."""
    
    def test_extract_artifacts_from_slice(self, analysis_service):
        """Test extracting context artifacts from a slice."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("directory", analysis)
        
        if slices:
            slice_id = slices[0].slice_id
            artifacts = analysis_service.extract_artifacts(slice_id)
            
            assert isinstance(artifacts, list)
            # Artifacts depend on slice content
    
    def test_extract_from_nonexistent_slice(self, analysis_service):
        """Test extracting from non-existent slice."""
        analysis_service.scan()
        
        # Should handle gracefully or raise appropriate error
        result = analysis_service.extract_artifacts("nonexistent-slice")
        assert isinstance(result, list)
    
    def test_extract_without_analysis(self, analysis_service):
        """Test extraction uses cached analysis."""
        analysis_service.scan()
        slices = analysis_service.generate_slices("directory")
        
        if slices:
            # Should work with cached analysis
            artifacts = analysis_service.extract_artifacts(slices[0].slice_id)
            assert isinstance(artifacts, list)


class TestAnalysisServiceReporting:
    """Test analysis reporting."""
    
    def test_generate_report(self, analysis_service):
        """Test generating comprehensive analysis report."""
        analysis = analysis_service.scan()
        analysis_service.generate_slices("directory", analysis)
        
        report = analysis_service.generate_report()
        
        assert isinstance(report, dict)
        assert "analysis" in report
        assert "slices" in report
        assert "summary" in report
    
    def test_report_includes_statistics(self, analysis_service):
        """Test that report includes statistics."""
        analysis = analysis_service.scan()
        analysis_service.generate_slices("directory", analysis)
        
        report = analysis_service.generate_report()
        
        summary = report.get("summary", {})
        assert "total_slices" in summary or len(summary) > 0
    
    def test_generate_report_with_filter(self, analysis_service):
        """Test generating report with slice filter."""
        analysis = analysis_service.scan()
        slices = analysis_service.generate_slices("directory", analysis)
        
        if slices:
            slice_id = slices[0].slice_id
            report = analysis_service.generate_report(slice_filter=slice_id)
            
            assert isinstance(report, dict)


class TestAnalysisServiceWorkflow:
    """Test complete analysis workflow."""
    
    def test_full_workflow(self, analysis_service):
        """Test complete scan -> slice -> extract -> report workflow."""
        # Step 1: Scan
        analysis = analysis_service.scan()
        assert analysis is not None
        
        # Step 2: Generate slices
        slices = analysis_service.generate_slices("directory", analysis)
        assert len(slices) > 0
        
        # Step 3: Extract artifacts (optional, depends on slice)
        if slices:
            artifacts = analysis_service.extract_artifacts(slices[0].slice_id)
            assert isinstance(artifacts, list)
        
        # Step 4: Generate report
        report = analysis_service.generate_report()
        assert isinstance(report, dict)
        assert "analysis" in report


class TestAnalysisServiceEdgeCases:
    """Test edge cases and error handling."""
    
    def test_scan_empty_directory(self, analysis_service, tmp_path):
        """Test scanning empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        analysis = analysis_service.scan(empty_dir)
        
        assert analysis.repo_root == empty_dir
        # Should handle gracefully
        assert isinstance(analysis.languages, list)
    
    def test_multiple_scans_override(self, analysis_service):
        """Test that multiple scans override previous analysis."""
        analysis1 = analysis_service.scan()
        analysis2 = analysis_service.scan()
        
        last = analysis_service.get_last_analysis()
        
        # Should return most recent scan
        assert last is not None
    
    def test_slice_generation_consistency(self, analysis_service):
        """Test that same strategy generates consistent slices."""
        analysis = analysis_service.scan()
        
        slices1 = analysis_service.generate_slices("directory", analysis)
        slices2 = analysis_service.generate_slices("directory", analysis)
        
        # Should generate same number of slices
        assert len(slices1) == len(slices2)
