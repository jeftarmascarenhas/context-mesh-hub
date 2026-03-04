"""MCP Tool: cm_status - Project status.

Tool 8 of 8: Get complete Context Mesh project status.
"""

from typing import Dict, Any

from fastmcp import FastMCP

from ...loader import ContextLoader
from ...validator import ContextValidator
from ...infrastructure.persistence.plan_repository import PlanRepository
from ...infrastructure.persistence.proposal_repository import ProposalRepository
from ..decorators import handle_mcp_errors


def register_cm_status(
    mcp: FastMCP,
    loader: ContextLoader,
    validator: ContextValidator,
    plan_repository: PlanRepository,
    proposal_repository: ProposalRepository,
):
    """Register cm_status tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        loader: ContextLoader instance
        validator: ContextValidator instance
        plan_repository: PlanRepository instance
        proposal_repository: ProposalRepository instance
    """
    
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_status() -> Dict[str, Any]:
        """Get complete Context Mesh project status.
        
        Returns comprehensive status including:
        - Project health and lifecycle state
        - Artifact counts and status
        - Validation results
        - Suggested next actions
        - Workflow guidance
        
        This is the primary status tool - use it to understand project state
        and get guidance on next steps.
        
        Returns:
            Dictionary with:
            - project: Basic project info and initialization status
            - artifacts: Counts of all artifact types
            - health: Validation status and issues
            - lifecycle: Current phase and blockers
            - suggestions: Prioritized next actions
            - workflow: Phase-specific guidance
        
        Examples:
            # Get status of current project
            cm_status()
        """
        index = loader.index
        
        # Project info
        has_project_intent = index.get("project_intent") is not None
        
        # Count artifacts
        features = index.get("feature_intents", {})
        decisions = index.get("decisions", {})
        agents = index.get("agents", {})
        patterns = index.get("knowledge", {}).get("patterns", {})
        anti_patterns = index.get("knowledge", {}).get("anti-patterns", {})
        
        # Get validation status
        validation = validator.validate()
        
        # Determine lifecycle phase
        if not has_project_intent:
            phase = "uninitialized"
            next_actions = [
                "Run cm_init(action='new') to initialize Context Mesh",
                "Or cm_init(action='existing') for brownfield setup",
            ]
        elif len(features) == 0:
            phase = "initialized"
            next_actions = [
                "Create features: cm_intent(action='create', type='feature')",
                "Add decisions: cm_intent(action='create', type='decision')",
            ]
        elif len(decisions) == 0:
            phase = "intent_defined"
            next_actions = [
                "Document technical decisions for features",
                "Run cm_validate() to check cross-references",
            ]
        else:
            phase = "active"
            next_actions = [
                "Use cm_build(action='plan') to create build plans",
                "Use cm_analyze(action='scan') for brownfield analysis",
                "Run cm_validate() regularly to maintain quality",
            ]
        
        # Feature status breakdown
        feature_status_counts = {}
        for feat_name, artifact in features.items():
            content = artifact.get("content", "")
            status = "Unknown"
            for line in content.split("\n"):
                if "Status**:" in line or "Status:" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        status = parts[-1].strip()
                        break
            feature_status_counts[status] = feature_status_counts.get(status, 0) + 1
        
        return {
            "project": {
                "initialized": has_project_intent,
                "repo_root": str(loader.repo_root),
                "context_dir": str(loader.context_dir),
                "phase": phase,
            },
            "artifacts": {
                "features": len(features),
                "decisions": len(decisions),
                "agents": len(agents),
                "patterns": len(patterns),
                "anti_patterns": len(anti_patterns),
                "feature_status": feature_status_counts,
            },
            "health": {
                "valid": validation["valid"],
                "errors": len(validation.get("errors", [])),
                "warnings": len(validation.get("warnings", [])),
                "top_issues": validation.get("errors", [])[:3] + validation.get("warnings", [])[:3],
            },
            "suggestions": next_actions,
            "workflow": {
                "current_phase": phase,
                "description": _get_phase_description(phase),
            },
        }


def _get_phase_description(phase: str) -> str:
    """Get description for lifecycle phase."""
    descriptions = {
        "uninitialized": "Project not yet initialized with Context Mesh",
        "initialized": "Context Mesh initialized, ready to add features",
        "intent_defined": "Features defined, add technical decisions",
        "active": "Active development with features and decisions",
    }
    return descriptions.get(phase, "Unknown phase")
