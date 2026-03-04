"""Tests for domain services.

Tests all domain services with dependency injection and mocks.
Focuses on business logic without I/O operations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from hub_core.domain.services.intent_service import IntentService
from hub_core.shared.errors import ArtifactNotFoundError, ValidationError


class TestIntentService:
    """Test IntentService functionality."""
    
    def test_create_feature(self, intent_service):
        """Test feature creation."""
        result = intent_service.create_feature(
            title="User Authentication",
            what="JWT-based auth system",
            why="Secure user access",
            acceptance_criteria=["Users can log in", "Tokens are issued"],
            related_decisions=["D001"]
        )
        
        assert result["id"].startswith("F")
        assert "file_path" in result
        assert "file_content" in result
        assert "User Authentication" in result["file_content"]
        assert "JWT-based auth system" in result["file_content"]
        assert "D001" in result["file_content"]
    
    def test_create_feature_slugification(self, intent_service):
        """Test that feature titles are properly slugified."""
        result = intent_service.create_feature(
            title="My Complex Feature Title!",
            what="Test",
            why="Test"
        )
        
        assert "my-complex-feature-title" in result["file_path"]
    
    def test_list_features(self, intent_service):
        """Test listing all features."""
        features = intent_service.list_features()
        
        assert isinstance(features, list)
        assert len(features) > 0
        
        # Check feature structure
        feature = features[0]
        assert "name" in feature
        assert "path" in feature
        assert "status" in feature
        assert "title" in feature
    
    def test_get_feature_by_id(self, intent_service):
        """Test getting a feature by ID."""
        # First list features to get a valid ID
        features = intent_service.list_features()
        if not features:
            pytest.skip("No features available for testing")
        
        feature_id = features[0]["name"]
        result = intent_service.get_feature(feature_id)
        
        assert result["name"] == feature_id
        assert "content" in result
        assert "status" in result
        assert "title" in result
    
    def test_get_feature_not_found(self, intent_service):
        """Test getting non-existent feature raises error."""
        with pytest.raises(ArtifactNotFoundError) as exc_info:
            intent_service.get_feature("F9999")
        
        assert "not found" in str(exc_info.value).lower() or "F9999" in str(exc_info.value)
    
    def test_create_decision(self, intent_service):
        """Test decision creation."""
        result = intent_service.create_decision(
            title="Test Technology Stack",
            context="Need to choose tech stack",
            decision="Use Python 3.12+",
            rationale="Python is mature and well-supported",
            alternatives=[
                {"name": "Node.js", "reason": "Less MCP ecosystem support"}
            ],
            consequences={
                "positive": ["Strong ecosystem", "Type hints"],
                "tradeoffs": ["GIL limitations"]
            }
        )
        
        assert result["id"].startswith("D")
        assert "file_path" in result
        assert "file_content" in result
        assert "Test Technology Stack" in result["file_content"]
        assert "Python 3.12+" in result["file_content"]
        assert "Node.js" in result["file_content"]
    
    def test_list_decisions(self, intent_service):
        """Test listing all decisions."""
        decisions = intent_service.list_decisions()
        
        assert isinstance(decisions, list)
        assert len(decisions) > 0
        
        # Check decision structure
        decision = decisions[0]
        assert "number" in decision  # list_decisions returns 'number' not 'name'
        assert "path" in decision
        assert "status" in decision
        assert "title" in decision
    
    def test_get_decision(self, intent_service):
        """Test getting a decision."""
        decisions = intent_service.list_decisions()
        if not decisions:
            pytest.skip("No decisions available for testing")
        
        decision_id = decisions[0]["number"]  # Use 'number' field
        result = intent_service.get_decision(decision_id)
        
        assert result["name"] == decision_id
        assert "content" in result
        assert "status" in result
    
    def test_get_project_intent(self, intent_service):
        """Test getting project intent."""
        result = intent_service.get_project_intent()
        
        assert "content" in result
        assert "path" in result
        # Project intent should have title
        assert len(result["content"]) > 0


class TestIntentServiceHelpers:
    """Test IntentService helper methods."""
    
    def test_slugify(self, intent_service):
        """Test slug generation."""
        slug = intent_service._slugify("My Feature Title!")
        assert slug == "my-feature-title"
        
        slug2 = intent_service._slugify("API & Database Integration")
        assert "&" not in slug2
        assert slug2 == "api-database-integration"
    
    def test_get_next_feature_number(self, intent_service):
        """Test getting next feature number."""
        index = intent_service.loader.index
        next_num = intent_service._get_next_feature_number(index)
        
        assert next_num.startswith("F")
        assert len(next_num) == 4  # F001 format
        assert next_num[1:].isdigit()
    
    def test_get_next_decision_number(self, intent_service):
        """Test getting next decision number."""
        index = intent_service.loader.index
        next_num = intent_service._get_next_decision_number(index)
        
        assert next_num.startswith("D")
        assert len(next_num) == 4  # D001 format
        assert next_num[1:].isdigit()


class TestIntentServiceEdgeCases:
    """Test edge cases and error handling."""
    
    def test_create_feature_minimal(self, intent_service):
        """Test creating feature with minimal data."""
        result = intent_service.create_feature(
            title="Minimal Feature",
            what="Test",
            why="Test"
        )
        
        assert result["file_content"] is not None
        assert "Minimal Feature" in result["file_content"]
    
    def test_create_feature_empty_title(self, intent_service):
        """Test creating feature with empty title."""
        result = intent_service.create_feature(
            title="",
            what="Test",
            why="Test"
        )
        
        # Should handle gracefully
        assert result["file_path"] is not None
    
    def test_update_feature_sections(self, intent_service):
        """Test updating feature sections."""
        features = intent_service.list_features()
        if not features:
            pytest.skip("No features available for testing")
        
        feature_id = features[0]["name"]
        result = intent_service.update_feature(
            feature_id,
            {"What": "Updated what section"}
        )
        
        assert "updated_content" in result
        assert "Updated what section" in result["updated_content"]
