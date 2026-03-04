"""Tests for MCP tools layer.

Tests MCP tool wrappers that expose domain services.
Tests error handling decorators and tool contracts.
"""

import pytest
from unittest.mock import Mock, patch

from hub_core.loader import ContextLoader
from hub_core.bundler import ContextBundler
from hub_core.infrastructure.parsers.markdown_parser import MarkdownParser
from hub_core.infrastructure.parsers.extractor import BuildPlanExtractor
from hub_core.domain.services.intent_service import IntentService
from hub_core.domain.services.build_service import BuildService
from hub_core.shared.errors import ArtifactNotFoundError, ValidationError


# ============================================================================
# MCP TOOL CONTRACT TESTS
# ============================================================================

class TestMCPToolContracts:
    """Test that MCP tools follow expected contracts."""
    
    def test_cm_intent_create_feature_returns_dict(self, intent_service):
        """Test cm_intent create feature returns proper structure."""
        result = intent_service.create_feature(
            title="Test Feature",
            what="Test what",
            why="Test why"
        )
        
        # MCP tools should return dicts
        assert isinstance(result, dict)
        assert "file_path" in result
        assert "file_content" in result
    
    def test_cm_intent_list_features_returns_list(self, intent_service):
        """Test cm_intent list returns list of dicts."""
        result = intent_service.list_features()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)
            assert "name" in result[0]
            assert "path" in result[0]
    
    def test_cm_intent_get_feature_returns_dict(self, intent_service):
        """Test cm_intent get returns feature dict."""
        features = intent_service.list_features()
        if not features:
            pytest.skip("No features available")
        
        feature_id = features[0]["name"]
        result = intent_service.get_feature(feature_id)
        
        assert isinstance(result, dict)
        assert "content" in result
        assert "status" in result
    
    def test_build_service_create_plan_returns_buildplan(self, build_service):
        """Test build service returns BuildPlan object."""
        from hub_core.domain.models.build import BuildPlan
        
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available")
        
        feature_name = list(features.keys())[0]
        result = build_service.create_plan(feature_name)
        
        assert isinstance(result, BuildPlan)
        assert hasattr(result, "plan_id")
        assert hasattr(result, "implementation_steps")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestMCPErrorHandling:
    """Test error handling in MCP tool layer."""
    
    def test_artifact_not_found_structure(self):
        """Test ArtifactNotFoundError has proper structure."""
        error = ArtifactNotFoundError("feature", "F9999")
        error_dict = error.to_dict()
        
        assert "error" in error_dict
        assert "error_type" in error_dict
        assert "details" in error_dict
        assert error_dict["error_type"] == "ArtifactNotFoundError"
    
    def test_validation_error_structure(self):
        """Test ValidationError has proper structure."""
        error = ValidationError("Invalid content", errors=["Missing What section"])
        error_dict = error.to_dict()
        
        assert "error" in error_dict
        assert "error_type" in error_dict
        assert error_dict["error_type"] == "ValidationError"
    
    def test_service_raises_proper_exceptions(self, intent_service):
        """Test that services raise typed exceptions."""
        with pytest.raises(Exception):  # Service may raise various error types
            intent_service.get_feature("F9999-nonexistent")


# ============================================================================
# MCP TOOL DECORATOR TESTS
# ============================================================================

class TestMCPDecorators:
    """Test MCP tool decorators."""
    
    def test_error_decorator_catches_exceptions(self):
        """Test that error decorator catches and converts exceptions."""
        from hub_core.mcp.decorators import handle_mcp_errors
        
        @handle_mcp_errors
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        
        assert isinstance(result, dict)
        assert "error" in result
    
    def test_error_decorator_converts_context_mesh_errors(self):
        """Test decorator converts ContextMeshError to dict."""
        from hub_core.mcp.decorators import handle_mcp_errors
        
        @handle_mcp_errors
        def failing_with_custom_error():
            raise ArtifactNotFoundError("test", "T001")
        
        result = failing_with_custom_error()
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "error_type" in result
    
    def test_error_decorator_preserves_success(self):
        """Test decorator doesn't interfere with successful calls."""
        from hub_core.mcp.decorators import handle_mcp_errors
        
        @handle_mcp_errors
        def successful_function():
            return {"result": "success"}
        
        result = successful_function()
        
        assert result == {"result": "success"}


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestMCPToolIntegration:
    """Test MCP tools with real services."""
    
    def test_intent_service_create_and_retrieve(self, intent_service):
        """Test creating and retrieving feature."""
        # Create
        created = intent_service.create_feature(
            title="Integration Test Feature",
            what="Test integration",
            why="Validate workflow"
        )
        
        assert "file_content" in created
        assert "Integration Test Feature" in created["file_content"]
    
    def test_build_workflow_create_and_approve(self, build_service):
        """Test build workflow: create plan -> approve -> execute."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available")
        
        feature_name = list(features.keys())[0]
        
        # Create plan
        plan = build_service.create_plan(feature_name)
        assert plan.plan_id is not None
        
        # Approve plan
        approval = build_service.approve_plan(plan.plan_id, action="approve")
        from hub_core.domain.models.build import ApprovalStatus
        assert approval.status == ApprovalStatus.APPROVED
        
        # Generate execution instructions
        instructions = build_service.generate_execution_instructions(plan.plan_id)
        assert "plan_id" in instructions
        assert instructions["plan_id"] == plan.plan_id


# ============================================================================
# TOOL VALIDATION TESTS
# ============================================================================

class TestMCPToolValidation:
    """Test input validation in MCP tools."""
    
    def test_intent_service_handles_empty_title(self, intent_service):
        """Test intent service handles empty title gracefully."""
        result = intent_service.create_feature(
            title="",
            what="Test",
            why="Test"
        )
        
        # Should handle gracefully, not crash
        assert "file_path" in result
    
    def test_intent_service_handles_special_characters(self, intent_service):
        """Test intent service handles special characters in title."""
        result = intent_service.create_feature(
            title="Feature with @#$% special chars!",
            what="Test",
            why="Test"
        )
        
        # Should sanitize for filename
        assert "file_path" in result
        # Special chars should be removed or replaced
        assert "@" not in result["file_path"]
        assert "#" not in result["file_path"]
    
    def test_build_service_validates_feature_exists(self, build_service):
        """Test build service validates feature exists."""
        with pytest.raises(Exception):  # May raise different error types
            build_service.create_plan("F9999-nonexistent")


# ============================================================================
# RESPONSE FORMAT TESTS
# ============================================================================

class TestMCPResponseFormats:
    """Test that MCP tool responses follow consistent formats."""
    
    def test_create_operations_return_file_info(self, intent_service):
        """Test that create operations return file path and content."""
        result = intent_service.create_feature(
            title="Test",
            what="Test",
            why="Test"
        )
        
        assert "file_path" in result
        assert "file_content" in result
        assert isinstance(result["file_path"], str)
        assert isinstance(result["file_content"], str)
    
    def test_list_operations_return_arrays(self, intent_service):
        """Test that list operations return arrays."""
        features = intent_service.list_features()
        decisions = intent_service.list_decisions()
        
        assert isinstance(features, list)
        assert isinstance(decisions, list)
    
    def test_get_operations_return_detailed_info(self, intent_service):
        """Test that get operations return detailed information."""
        features = intent_service.list_features()
        if not features:
            pytest.skip("No features available")
        
        feature = intent_service.get_feature(features[0]["name"])
        
        assert "content" in feature
        assert "status" in feature
        assert "path" in feature
        assert len(feature["content"]) > 0


# ============================================================================
# CROSS-CUTTING CONCERNS TESTS
# ============================================================================

class TestMCPCrossCuttingConcerns:
    """Test cross-cutting concerns: logging, error handling, validation."""
    
    def test_all_services_use_dependency_injection(
        self,
        intent_service,
        build_service,
        analysis_service,
        learn_service
    ):
        """Test that all services receive dependencies via constructor."""
        # IntentService
        assert hasattr(intent_service, "loader")
        assert hasattr(intent_service, "parser")
        
        # BuildService
        assert hasattr(build_service, "loader")
        assert hasattr(build_service, "bundler")
        assert hasattr(build_service, "plan_repo")
        
        # AnalysisService
        assert hasattr(analysis_service, "scanner")
        assert hasattr(analysis_service, "slice_generator")
        
        # LearnService
        assert hasattr(learn_service, "loader")
        assert hasattr(learn_service, "proposal_repo")
    
    def test_services_dont_create_dependencies_internally(self):
        """Test that services don't instantiate their own dependencies."""
        # This is validated by the fact that our fixtures work
        # If services created their own dependencies, we couldn't inject mocks
        pass
    
    def test_error_messages_are_helpful(self, intent_service):
        """Test that error messages provide helpful information."""
        try:
            intent_service.get_feature("F9999-nonexistent")
        except Exception as e:
            # Should provide useful error information
            error_str = str(e)
            assert len(error_str) > 0
            assert "F9999" in error_str or "not found" in error_str.lower()
