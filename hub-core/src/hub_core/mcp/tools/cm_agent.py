"""MCP Tool: cm_agent - Agent management.

Tool 3 of 8: CRUD for execution agents.
"""

from typing import Optional, Dict, Any

from fastmcp import FastMCP

from ...domain.services.intent_service import IntentService
from ..decorators import handle_mcp_errors


def register_cm_agent(
    mcp: FastMCP,
    intent_service: IntentService,
):
    """Register cm_agent tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        intent_service: IntentService instance
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
    def cm_agent(
        action: str,
        name: Optional[str] = None,
        content: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Manage execution agents.
        
        Agents are reusable execution patterns that reference context files.
        
        Args:
            action: Action to perform - "create", "update", "get", "list", "delete"
            name: Agent name (required for get/update/delete)
            content: Content dict for create/update:
                - purpose: What the agent does
                - context_files: List of files to load
                - steps: Execution steps
                - dod: Definition of Done criteria
        
        Returns:
            Dictionary with operation result
        
        Examples:
            # Create an agent
            cm_agent(action="create", name="api-developer", content={
                "purpose": "Implement REST API endpoints",
                "context_files": ["@context/decisions/D001-*.md"],
                "steps": ["Read API spec", "Implement endpoint", "Add tests"],
                "dod": ["All tests pass", "API documented"]
            })
            
            # List all agents
            cm_agent(action="list")
        """
        valid_actions = ["create", "update", "get", "list", "delete"]
        if action not in valid_actions:
            return {"error": f"Invalid action: {action}", "valid_actions": valid_actions}
        
        # ====================================================================
        # ACTION: LIST
        # ====================================================================
        if action == "list":
            agents = intent_service.list_agents()
            return {
                "action": "list",
                "total": len(agents),
                "agents": agents,
            }
        
        # ====================================================================
        # ACTION: GET
        # ====================================================================
        elif action == "get":
            if not name:
                return {"error": "Name required for get action"}
            
            result = intent_service.get_agent(name)
            return {
                "action": "get",
                "name": result["name"],
                "path": result["path"],
                "content": result["content"],
            }
        
        # ====================================================================
        # ACTION: CREATE
        # ====================================================================
        elif action == "create":
            if not name:
                return {"error": "Name required for create action"}
            if not content:
                return {"error": "Content required for create action"}
            
            # Normalize name (add agent- prefix if missing)
            if not name.startswith("agent-"):
                name = f"agent-{name}"
            
            purpose = content.get("purpose", "_What this agent does_")
            context_files = content.get("context_files", [])
            steps = content.get("steps", [])
            dod = content.get("dod", [])
            
            # Build agent content
            context_section = "\n".join(f"- `{cf}`" for cf in context_files) if context_files else "_No context files specified_"
            steps_section = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps)) if steps else "_No steps specified_"
            dod_section = "\n".join(f"- [ ] {item}" for item in dod) if dod else "_No DoD specified_"
            
            file_content = f"""# Agent: {name}

## Purpose

{purpose}

## Context Files to Load

{context_section}

## Execution Steps

{steps_section}

## Definition of Done

{dod_section}

## Usage

```
Load this agent and execute steps in order.
Check Definition of Done before marking complete.
```
"""
            
            return {
                "action": "create",
                "name": name,
                "file_path": f"context/agents/{name}.md",
                "file_content": file_content,
            }
        
        # ====================================================================
        # ACTION: UPDATE / DELETE
        # ====================================================================
        elif action in ["update", "delete"]:
            return {
                "error": f"{action.capitalize()} not yet implemented for agents",
                "tip": "Manually edit agent files in context/agents/",
            }
