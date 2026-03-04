"""MCP Tool: cm_build - Build protocol.

Tool 5 of 8: Bundle, plan, approve, and execute workflow.
"""

from typing import Optional, Dict, Any, List

from fastmcp import FastMCP

from ...domain.services.build_service import BuildService
from ...bundler import ContextBundler
from ..decorators import handle_mcp_errors


def register_cm_build(
    mcp: FastMCP,
    build_service: BuildService,
    bundler: ContextBundler,
):
    """Register cm_build tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        build_service: BuildService instance
        bundler: ContextBundler instance
    """
    
    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_build(
        action: str,
        identifier: Optional[str] = None,
        mode: Optional[str] = None,
        feedback: Optional[str] = None,
        scope: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Execute the build protocol: bundle context, plan, approve, and execute.
        
        Consolidates the build workflow into a single tool.
        
        Args:
            action: Action to perform - "bundle", "plan", "approve", "execute"
            identifier: Context identifier:
                - For "bundle": bundle type (e.g., "feature:F001")
                - For "plan": feature name (e.g., "F001")
                - For "approve"/"execute": plan ID
            mode: Mode for specific actions:
                - For "approve": "approve" or "reject"
                - For "execute": "instruction" or "assisted"
            feedback: Feedback message (for approve/reject)
            scope: List of step numbers for partial approval
        
        Returns:
            Dictionary with operation result:
            - For "bundle": bundled context content
            - For "plan": build plan with steps
            - For "approve": approval status
            - For "execute": execution instructions
        
        Examples:
            # Bundle project context
            cm_build(action="bundle", identifier="project")
            
            # Create build plan for feature
            cm_build(action="plan", identifier="F001")
            
            # Approve a plan
            cm_build(action="approve", identifier="plan-123", mode="approve")
            
            # Execute approved plan
            cm_build(action="execute", identifier="plan-123", mode="instruction")
        """
        valid_actions = ["bundle", "plan", "approve", "execute"]
        if action not in valid_actions:
            return {"error": f"Invalid action: {action}", "valid_actions": valid_actions}
        
        # ====================================================================
        # ACTION: BUNDLE
        # ====================================================================
        if action == "bundle":
            if not identifier:
                return {"error": "Identifier required for bundle action"}
            
            # Parse identifier (e.g., "project", "feature:F001", "decision:D001")
            if ":" in identifier:
                bundle_type, name = identifier.split(":", 1)
            else:
                bundle_type = identifier
                name = None
            
            if bundle_type == "project":
                content = bundler.bundle_project()
            elif bundle_type == "feature" and name:
                content = bundler.bundle_feature(name)
            elif bundle_type == "decision" and name:
                content = bundler.bundle_decision(name)
            else:
                return {
                    "error": f"Invalid bundle identifier: {identifier}",
                    "valid_formats": ["project", "feature:F001", "decision:D001"],
                }
            
            return {
                "action": "bundle",
                "identifier": identifier,
                "content": content,
            }
        
        # ====================================================================
        # ACTION: PLAN
        # ====================================================================
        elif action == "plan":
            if not identifier:
                return {"error": "Feature name required for plan action"}
            
            plan = build_service.create_plan(identifier)
            
            return {
                "action": "plan",
                "plan_id": plan.plan_id,
                "feature_name": plan.feature_name,
                "created_at": plan.created_at,
                "steps": [
                    {
                        "step_number": step.step_number,
                        "description": step.description,
                        "target_files": step.target_files,
                        "operations": step.operations,
                    }
                    for step in plan.implementation_steps
                ],
                "total_steps": len(plan.implementation_steps),
                "constraints": plan.constraints,
                "acceptance_criteria": plan.acceptance_criteria,
                "next_step": f"Use cm_build(action='approve', identifier='{plan.plan_id}', mode='approve') to approve",
            }
        
        # ====================================================================
        # ACTION: APPROVE
        # ====================================================================
        elif action == "approve":
            if not identifier:
                return {"error": "Plan ID required for approve action"}
            if not mode:
                return {"error": "Mode required (approve/reject)"}
            
            approval = build_service.approve_plan(
                plan_id=identifier,
                action=mode,
                scope=scope,
                feedback=feedback,
            )
            
            return {
                "action": "approve",
                "plan_id": approval.plan_id,
                "status": approval.status.value,
                "approved_at": approval.approved_at,
                "approved_scope": approval.approved_scope,
                "rejection_feedback": approval.rejection_feedback,
                "next_step": (
                    f"Use cm_build(action='execute', identifier='{identifier}') to get execution instructions"
                    if approval.status.value != "rejected" else None
                ),
            }
        
        # ====================================================================
        # ACTION: EXECUTE
        # ====================================================================
        elif action == "execute":
            if not identifier:
                return {"error": "Plan ID required for execute action"}
            
            execution_mode = mode or "instruction"
            instructions = build_service.generate_instructions(identifier, execution_mode)
            
            return {
                "action": "execute",
                "plan_id": identifier,
                "mode": execution_mode,
                "instructions": [
                    {
                        "instruction_id": inst.instruction_id,
                        "step_number": inst.step_number,
                        "operation": inst.operation,
                        "target_file": inst.target_file,
                        "description": inst.description,
                        "validation_check": inst.validation_check,
                    }
                    for inst in instructions
                ],
                "total_instructions": len(instructions),
            }
