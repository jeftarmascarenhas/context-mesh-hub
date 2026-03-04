"""MCP Tool: cm_validate - Context validation.

Tool 7 of 8: Validate Context Mesh repository structure and content.
"""

from typing import Dict, Any

from fastmcp import FastMCP

from ...validator import ContextValidator
from ...loader import ContextLoader
from ..decorators import handle_mcp_errors


def register_cm_validate(
    mcp: FastMCP,
    validator: ContextValidator,
    loader: ContextLoader,
):
    """Register cm_validate tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        validator: ContextValidator instance
        loader: ContextLoader instance
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
    def cm_validate() -> Dict[str, Any]:
        """Validate Context Mesh repository structure and content.
        
        Checks:
        - Required files exist (project-intent.md, AGENTS.md)
        - File naming conventions
        - Cross-references between artifacts
        - Status field consistency
        - Decision references in features
        
        Returns:
            Dictionary with:
            - valid: Boolean indicating overall validity
            - errors: List of critical issues that must be fixed
            - warnings: List of recommended improvements
            - info: List of informational messages
        
        Examples:
            # Validate current project
            cm_validate()
        """
        result = validator.validate()
        
        return {
            "valid": result["valid"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "info": result.get("info", []),
            "summary": {
                "total_errors": len(result.get("errors", [])),
                "total_warnings": len(result.get("warnings", [])),
                "total_info": len(result.get("info", [])),
            },
        }
