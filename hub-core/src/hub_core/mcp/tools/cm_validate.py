"""MCP Tool: cm_validate - Context validation.

Tool 7 of 8: Validate Context Mesh repository structure and content.
"""

from typing import Dict, Any

from fastmcp import FastMCP

from ...validator import ContextValidator
from ...enhanced_validator import EnhancedContextValidator
from ...loader import ContextLoader
from ...infrastructure.parsers.markdown_parser import MarkdownParser
from ..decorators import handle_mcp_errors


def register_cm_validate(
    mcp: FastMCP,
    validator: ContextValidator,
    loader: ContextLoader,
):
    """Register cm_validate tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        validator: ContextValidator instance (legacy, maintained for compatibility)
        loader: ContextLoader instance
    """
    
    # Create enhanced validator
    parser = MarkdownParser()
    enhanced_validator = EnhancedContextValidator(loader, parser)
    
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_validate() -> Dict[str, Any]:
        """Validate Context Mesh repository structure and content.
        
        Validates against ARTIFACT_SPECS.md specifications:
        
        **Naming Conventions:**
        - Features: F00X-description.md format
        - Decisions: D00X-description.md format
        - Agents: agent-name.md format
        - Patterns/Anti-patterns: lowercase-with-hyphens.md
        
        **Required Sections:**
        - Features: What, Why, Acceptance Criteria, Status
        - Decisions: Context, Decision, Rationale, Status
        - Project Intent: What, Why, Scope, Acceptance Criteria, Status
        - Patterns: Context, The Pattern, Evidence, Status
        - Anti-patterns: Context, The Problem, Evidence, Recommendation, Status
        - Agents: Purpose, Context Files to Load, Steps, Definition of Done
        
        **Status Field Format:**
        - Features: Active | Completed | Replaced | Abandoned
        - Decisions: Proposed | Accepted | Superseded | Deprecated
        - Must include Created date in YYYY-MM-DD format
        
        **Cross-References:**
        - All links must use relative paths
        - Referenced artifacts must exist
        - Decision/feature links validated
        
        Returns:
            Dictionary with:
            - valid: Boolean indicating overall validity
            - errors: List of critical issues that must be fixed
            - warnings: List of recommended improvements
            - info: List of informational messages
            - summary: Count of issues by type
        
        Examples:
            # Validate current project
            cm_validate()
        """
        # Use enhanced validator for comprehensive validation
        result = enhanced_validator.validate()
        
        # Convert to dictionary format
        return {
            "valid": result.valid,
            "errors": [e.to_dict() for e in result.errors],
            "warnings": [w.to_dict() for w in result.warnings],
            "info": [i.to_dict() for i in result.info],
            "summary": {
                "total_errors": len(result.errors),
                "total_warnings": len(result.warnings),
                "total_info": len(result.info),
            },
        }
