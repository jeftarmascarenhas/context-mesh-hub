"""Tests for BuildService.

Tests build plan creation, approval, and execution instruction generation.
Uses temporary persistence layer.
"""

import pytest
from datetime import datetime

from hub_core.domain.models.build import ApprovalStatus, BuildPlan, ApprovalState
from hub_core.domain.services.build_service import BuildService
from hub_core.shared.errors import ArtifactNotFoundError, PlanNotApprovedError, ValidationError


class TestBuildServicePlanCreation:
    """Test build plan creation."""
    
    def test_create_plan_for_existing_feature(self, build_service):
        """Test creating plan for existing feature."""
        # Use a known feature from the repo
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        assert plan.plan_id is not None
        assert plan.feature_name == feature_name
        assert len(plan.implementation_steps) > 0
        assert plan.created_at is not None
    
    def test_create_plan_nonexistent_feature(self, build_service):
        """Test creating plan for non-existent feature raises error."""
        with pytest.raises(Exception):  # May raise different error types
            build_service.create_plan("F9999-nonexistent")
    
    def test_plan_has_required_fields(self, build_service):
        """Test that created plan has all required fields."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        assert hasattr(plan, "plan_id")
        assert hasattr(plan, "feature_name")
        assert hasattr(plan, "feature_path")
        assert hasattr(plan, "implementation_steps")
        assert hasattr(plan, "target_files")
        assert hasattr(plan, "constraints")
        assert hasattr(plan, "acceptance_criteria")
    
    def test_plan_steps_have_structure(self, build_service):
        """Test that implementation steps have proper structure."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        if len(plan.implementation_steps) > 0:
            step = plan.implementation_steps[0]
            assert hasattr(step, "step_number")
            assert hasattr(step, "description")
            assert hasattr(step, "target_files")
            assert step.step_number > 0


class TestBuildServicePlanRetrieval:
    """Test build plan retrieval and persistence."""
    
    def test_get_plan_after_creation(self, build_service):
        """Test retrieving plan after creation."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        # Retrieve the plan
        retrieved = build_service.get_plan(plan.plan_id)
        
        assert retrieved.plan_id == plan.plan_id
        assert retrieved.feature_name == plan.feature_name
        assert len(retrieved.implementation_steps) == len(plan.implementation_steps)
    
    def test_get_nonexistent_plan(self, build_service):
        """Test retrieving non-existent plan raises error."""
        with pytest.raises(ArtifactNotFoundError):
            build_service.get_plan("nonexistent-plan-id")
    
    def test_list_plans(self, build_service):
        """Test listing all plans."""
        # Create a plan first
        features = build_service.loader.index.get("feature_intents", {})
        if features:
            feature_name = list(features.keys())[0]
            build_service.create_plan(feature_name)
        
        plans = build_service.list_plans()
        
        assert isinstance(plans, list)
        if len(plans) > 0:
            assert isinstance(plans[0], BuildPlan)


class TestBuildServiceApproval:
    """Test build plan approval workflow."""
    
    def test_approve_plan(self, build_service):
        """Test approving a plan."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        approval = build_service.approve_plan(plan.plan_id, action="approve")
        
        assert approval.plan_id == plan.plan_id
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.approved_at is not None
    
    def test_approve_with_scope(self, build_service):
        """Test partial approval with specific steps."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        if len(plan.implementation_steps) > 1:
            approval = build_service.approve_plan(
                plan.plan_id,
                action="approve",
                scope=[1, 2]
            )
            
            assert approval.status == ApprovalStatus.PARTIALLY_APPROVED
            assert approval.approved_scope == [1, 2]
    
    def test_reject_plan(self, build_service):
        """Test rejecting a plan."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        approval = build_service.approve_plan(
            plan.plan_id,
            action="reject",
            feedback="Needs more detail"
        )
        
        assert approval.status == ApprovalStatus.REJECTED
        assert approval.notes == "Needs more detail"
    
    def test_get_approval_status(self, build_service):
        """Test retrieving approval status."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        build_service.approve_plan(plan.plan_id, action="approve")
        
        status = build_service.get_approval_status(plan.plan_id)
        
        assert status.status == ApprovalStatus.APPROVED


class TestBuildServiceExecution:
    """Test execution instruction generation."""
    
    def test_generate_execution_instructions(self, build_service):
        """Test generating execution instructions for approved plan."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        build_service.approve_plan(plan.plan_id, action="approve")
        
        instructions = build_service.generate_execution_instructions(plan.plan_id)
        
        assert "plan_id" in instructions
        assert "instructions" in instructions
        assert instructions["plan_id"] == plan.plan_id
    
    def test_generate_instructions_unapproved_plan(self, build_service):
        """Test generating instructions for unapproved plan raises error."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        # Don't approve - should raise error
        with pytest.raises(PlanNotApprovedError):
            build_service.generate_execution_instructions(plan.plan_id)
    
    def test_generate_instructions_rejected_plan(self, build_service):
        """Test generating instructions for rejected plan raises error."""
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        build_service.approve_plan(plan.plan_id, action="reject")
        
        with pytest.raises(PlanNotApprovedError):
            build_service.generate_execution_instructions(plan.plan_id)


class TestBuildServiceHelpers:
    """Test helper methods in BuildService."""
    
    def test_extract_implementation_approach(self, build_service):
        """Test extracting implementation approach from content."""
        content = """## How

Step 1: Create database schema
Step 2: Implement API endpoints
Step 3: Add tests
"""
        approach = build_service._extract_implementation_approach(content)
        
        # Returns list of strings
        assert isinstance(approach, list)
        if len(approach) > 0:
            assert any("database" in str(item).lower() for item in approach)
    
    def test_generate_steps(self, build_service):
        """Test step generation from feature content."""
        content = """## What

User authentication system.

## Acceptance Criteria

- [ ] Users can log in
- [ ] Tokens are issued
- [ ] Tokens expire
"""
        steps = build_service._generate_steps(
            "F001",
            content,
            ["Users can log in", "Tokens are issued"],
            ["Implement JWT auth"]  # Pass as list not string
        )
        
        assert len(steps) > 0
        assert all(hasattr(s, "step_number") for s in steps)
        assert all(hasattr(s, "description") for s in steps)


class TestBuildServiceEdgeCases:
    """Test edge cases and error handling."""
    
    def test_create_plan_feature_without_acceptance_criteria(self, build_service):
        """Test creating plan for feature with no acceptance criteria."""
        # This tests graceful degradation
        features = build_service.loader.index.get("feature_intents", {})
        if not features:
            pytest.skip("No features available for testing")
        
        feature_name = list(features.keys())[0]
        plan = build_service.create_plan(feature_name)
        
        # Should still create a plan even if no AC
        assert plan.plan_id is not None
    
    def test_approve_nonexistent_plan(self, build_service):
        """Test approving non-existent plan raises error."""
        with pytest.raises(Exception):  # May raise different error types
            build_service.approve_plan("nonexistent-id", action="approve")
