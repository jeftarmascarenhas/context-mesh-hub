"""MCP Client for connecting to Context Mesh Hub server.

Updated for MCP Simplification (D013): 8 consolidated tools.
Provides backward compatibility mapping from old tool names to new tools.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel


# Tool mapping for backward compatibility (D013 MCP Simplification)
# Maps old tool names to new consolidated tool + action/type
TOOL_MIGRATION_MAP: dict[str, dict[str, Any]] = {
    # cm_init consolidates project initialization
    "cm_new_project": {"tool": "cm_init", "params": {"action": "new"}},
    "cm_existing_project": {"tool": "cm_init", "params": {"action": "existing"}},
    
    # cm_intent consolidates feature/decision/bug CRUD
    "cm_add_feature": {"tool": "cm_intent", "params": {"action": "create", "type": "feature"}},
    "cm_update_feature": {"tool": "cm_intent", "params": {"action": "update", "type": "feature"}},
    "cm_list_features": {"tool": "cm_intent", "params": {"action": "list", "type": "feature"}},
    "cm_fix_bug": {"tool": "cm_intent", "params": {"action": "create", "type": "bug"}},
    "cm_create_decision": {"tool": "cm_intent", "params": {"action": "create", "type": "decision"}},
    "intent_add_feature": {"tool": "cm_intent", "params": {"action": "create", "type": "feature"}},
    "context_read": {"tool": "cm_intent", "params": {"action": "get"}},
    
    # cm_agent consolidates agent management
    "cm_create_agent": {"tool": "cm_agent", "params": {"action": "create"}},
    "intent_create_agent": {"tool": "cm_agent", "params": {"action": "create"}},
    
    # cm_build consolidates build protocol
    "build_plan": {"tool": "cm_build", "params": {"action": "plan"}},
    "build_approve": {"tool": "cm_build", "params": {"action": "approve"}},
    "build_execute": {"tool": "cm_build", "params": {"action": "execute"}},
    "context_bundle": {"tool": "cm_build", "params": {"action": "bundle"}},
    
    # cm_validate is standalone
    "context_validate": {"tool": "cm_validate", "params": {}},
    
    # cm_analyze consolidates brownfield/analysis
    "brownfield_scan": {"tool": "cm_analyze", "params": {"action": "scan"}},
    "brownfield_slice": {"tool": "cm_analyze", "params": {"action": "slice"}},
    "brownfield_extract": {"tool": "cm_analyze", "params": {"action": "extract"}},
    "brownfield_report": {"tool": "cm_analyze", "params": {"action": "report"}},
    
    # cm_learn consolidates learn sync
    "learn_sync_initiate": {"tool": "cm_learn", "params": {"action": "initiate"}},
    "learn_sync_review": {"tool": "cm_learn", "params": {"action": "review"}},
    "learn_sync_accept": {"tool": "cm_learn", "params": {"action": "accept"}},
    "learn_sync_apply": {"tool": "cm_learn", "params": {"action": "apply"}},
    
    # cm_status consolidates status tools
    "cm_status": {"tool": "cm_status", "params": {}},
    "hub_health": {"tool": "cm_status", "params": {}},
    "cm_lifecycle_state": {"tool": "cm_status", "params": {}},
    "cm_suggest_next": {"tool": "cm_status", "params": {}},
    "cm_workflow_guide": {"tool": "cm_status", "params": {}},
}

# New consolidated tools (8 total per D013)
CONSOLIDATED_TOOLS = {
    "cm_init",      # actions: new, existing, migrate
    "cm_intent",    # actions: create, update, get, list, delete; types: feature, decision, bug
    "cm_agent",     # actions: create, update, get, list, delete
    "cm_build",     # actions: bundle, plan, approve, execute
    "cm_validate",  # structure, links, status validation
    "cm_analyze",   # actions: scan, slice, extract, report, impact, dependencies
    "cm_learn",     # actions: initiate, review, accept, apply
    "cm_status",    # overview, lifecycle, suggestions
}


class MCPToolResult(BaseModel):
    """Result from an MCP tool call."""
    
    success: bool
    content: Any
    error: Optional[str] = None
    migrated_from: Optional[str] = None  # Track if tool was migrated


class MCPClient:
    """Client for interacting with the Context Mesh Hub MCP server.
    
    This client can operate in two modes:
    1. Direct mode: Import and call hub_core directly (for local development)
    2. Subprocess mode: Spawn the MCP server and communicate via stdio
    
    Updated for MCP Simplification (D013): Supports both old and new tool names.
    Old tool names are automatically mapped to new consolidated tools.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the MCP client.
        
        Args:
            repo_root: Path to the repository root. If None, uses current directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self._server_process: Optional[subprocess.Popen] = None
    
    def _migrate_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> tuple[str, dict[str, Any], Optional[str]]:
        """Migrate old tool names to new consolidated tools.
        
        Args:
            tool_name: Original tool name
            arguments: Original arguments
            
        Returns:
            Tuple of (new_tool_name, merged_arguments, old_tool_name_if_migrated)
        """
        if tool_name in CONSOLIDATED_TOOLS:
            # Already using new tool name
            return tool_name, arguments, None
        
        if tool_name in TOOL_MIGRATION_MAP:
            migration = TOOL_MIGRATION_MAP[tool_name]
            new_tool = migration["tool"]
            new_params = {**migration["params"], **arguments}
            return new_tool, new_params, tool_name
        
        # Unknown tool, pass through (server will handle error)
        return tool_name, arguments, None
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any] = None) -> MCPToolResult:
        """Call an MCP tool.
        
        Supports both old and new tool names. Old tool names are automatically
        migrated to the new consolidated tools per D013.
        
        Args:
            tool_name: Name of the tool to call (e.g., 'cm_status', 'cm_intent')
                       Old names like 'cm_add_feature' are still supported.
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPToolResult with the tool's response
        """
        arguments = arguments or {}
        
        # Migrate old tool names to new consolidated tools
        actual_tool, merged_args, migrated_from = self._migrate_tool_call(tool_name, arguments)
        
        try:
            # Try direct import first (for development)
            result = await self._call_tool_direct(actual_tool, merged_args)
            if migrated_from:
                result.migrated_from = migrated_from
            return result
        except ImportError:
            # Fall back to subprocess mode
            result = await self._call_tool_subprocess(actual_tool, merged_args)
            if migrated_from:
                result.migrated_from = migrated_from
            return result
    
    async def call_consolidated_tool(
        self, 
        tool: str, 
        action: Optional[str] = None,
        type: Optional[str] = None,
        **kwargs
    ) -> MCPToolResult:
        """Call a consolidated MCP tool with explicit action/type.
        
        This is the preferred method for calling the new 8 consolidated tools.
        
        Args:
            tool: One of cm_init, cm_intent, cm_agent, cm_build, cm_validate,
                  cm_analyze, cm_learn, cm_status
            action: Action to perform (e.g., 'create', 'update', 'list')
            type: Type of artifact (e.g., 'feature', 'decision', 'bug')
            **kwargs: Additional arguments for the tool
            
        Returns:
            MCPToolResult with the tool's response
            
        Examples:
            # Create a feature
            await client.call_consolidated_tool('cm_intent', action='create', type='feature', name='auth')
            
            # Create a build plan
            await client.call_consolidated_tool('cm_build', action='plan', feature_name='auth')
            
            # Initiate learn sync
            await client.call_consolidated_tool('cm_learn', action='initiate', feature_name='auth')
        """
        if tool not in CONSOLIDATED_TOOLS:
            return MCPToolResult(
                success=False, 
                content=None, 
                error=f"Unknown consolidated tool: {tool}. Valid tools: {', '.join(CONSOLIDATED_TOOLS)}"
            )
        
        arguments = {**kwargs}
        if action:
            arguments["action"] = action
        if type:
            arguments["type"] = type
        
        return await self.call_tool(tool, arguments)
    
    def _find_hub_core_path(self) -> Optional[Path]:
        """Find hub_core source path."""
        # Check multiple locations
        candidates = [
            self.repo_root / "hub-core" / "src",  # Same level
            self.repo_root.parent / "hub-core" / "src",  # Parent level
        ]
        for path in candidates:
            if path.exists():
                return path
        return None
    
    def _find_hub_core_dir(self) -> Optional[Path]:
        """Find hub-core project directory (for uv run)."""
        import os
        import platform
        
        # 1. Check environment variable
        hub_core_env = os.environ.get("CONTEXT_MESH_HUB_CORE_PATH")
        if hub_core_env:
            path = Path(hub_core_env)
            if path.name == "src" and (path.parent / "pyproject.toml").exists():
                return path.parent
            if (path / "pyproject.toml").exists():
                return path
        
        # 2. Check uv git cache (where uv tool install clones repos)
        # Windows: %LOCALAPPDATA%\uv\cache\git-v0\checkouts
        # macOS/Linux: ~/.cache/uv/git-v0/checkouts
        uv_cache_paths = []
        if platform.system() == "Windows":
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                uv_cache_paths.append(Path(local_app_data) / "uv" / "cache" / "git-v0" / "checkouts")
            uv_cache_paths.append(Path.home() / "AppData" / "Local" / "uv" / "cache" / "git-v0" / "checkouts")
        else:
            uv_cache_paths.append(Path.home() / ".cache" / "uv" / "git-v0" / "checkouts")
        
        for uv_git_cache in uv_cache_paths:
            if uv_git_cache.exists():
                try:
                    for repo_dir in uv_git_cache.iterdir():
                        if "context-mesh-hub" in repo_dir.name.lower():
                            for checkout in repo_dir.iterdir():
                                hub_core = checkout / "hub-core"
                                if (hub_core / "pyproject.toml").exists():
                                    return hub_core
                except (PermissionError, OSError):
                    continue
        
        # 3. Check local development paths
        candidates = [
            self.repo_root / "hub-core",
            self.repo_root.parent / "hub-core",
            Path.home() / "projects" / "context-mesh-hub" / "hub-core",
            Path.home() / "dev" / "context-mesh-hub" / "hub-core",
        ]
        
        # Windows-specific paths
        if platform.system() == "Windows":
            candidates.append(Path.home() / "source" / "repos" / "context-mesh-hub" / "hub-core")
        
        for path in candidates:
            if (path / "pyproject.toml").exists():
                return path
        
        return None
    
    async def _call_tool_direct(self, tool_name: str, arguments: dict[str, Any]) -> MCPToolResult:
        """Call tool by directly importing hub_core."""
        # Add hub-core to path if needed
        hub_core_path = self._find_hub_core_path()
        if hub_core_path and str(hub_core_path) not in sys.path:
            sys.path.insert(0, str(hub_core_path))
        
        from hub_core.server import create_server
        import inspect
        
        # Create server instance
        server = create_server(self.repo_root)
        
        # Find and call the tool
        # Tools are registered on the server, we need to find the right one
        for tool in server._tool_manager._tools.values():
            if tool.name == tool_name:
                # Call the tool function
                result = await tool.fn(**arguments) if inspect.iscoroutinefunction(tool.fn) else tool.fn(**arguments)
                return MCPToolResult(success=True, content=result)
        
        return MCPToolResult(success=False, content=None, error=f"Tool not found: {tool_name}")
    
    async def _call_tool_subprocess(self, tool_name: str, arguments: dict[str, Any]) -> MCPToolResult:
        """Call tool via subprocess (MCP protocol)."""
        # This is a simplified version - full MCP protocol would use stdio transport
        hub_core_path = self._find_hub_core_path()
        if not hub_core_path:
            return MCPToolResult(success=False, content=None, error="hub_core not found")
        
        try:
            # Run the tool via python -c
            code = f"""
import sys
import json
sys.path.insert(0, '{hub_core_path}')
from hub_core.tools import *

result = {tool_name}(**{json.dumps(arguments)})
print(json.dumps({{"success": True, "content": result}}))
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=30,
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return MCPToolResult(**data)
            else:
                return MCPToolResult(
                    success=False,
                    content=None,
                    error=result.stderr or "Unknown error"
                )
        except Exception as e:
            return MCPToolResult(success=False, content=None, error=str(e))
    
    async def list_tools(self) -> list[str]:
        """List available MCP tools."""
        try:
            hub_core_path = self.repo_root.parent / "hub-core" / "src"
            if hub_core_path.exists() and str(hub_core_path) not in sys.path:
                sys.path.insert(0, str(hub_core_path))
            
            from hub_core.server import create_server
            server = create_server(self.repo_root)
            
            return [tool.name for tool in server._tool_manager._tools.values()]
        except ImportError:
            return []
    
    def get_mcp_config(self, use_uv: bool = True) -> dict:
        """Get MCP configuration for AI editors.
        
        Args:
            use_uv: If True, use 'uv run' which auto-manages dependencies.
                   If False, use direct Python execution.
        """
        import os
        import shutil
        
        # Find hub-core directory
        hub_core_dir = self._find_hub_core_dir()
        
        # Check if uv is available and preferred
        uv_path = shutil.which("uv")
        
        if use_uv and uv_path and hub_core_dir:
            # Use uv run - auto-manages venv and dependencies
            return {
                "mcpServers": {
                    "context-mesh-hub": {
                        "command": uv_path,
                        "args": [
                            "run",
                            "--directory", str(hub_core_dir),
                            "python", "-m", "hub_core.server"
                        ]
                    }
                }
            }
        
        # Fallback: Find venv python (has fastmcp installed)
        def find_venv_python() -> str | None:
            # Check in hub project root
            hub_root = Path.home() / "Jeftar" / "hub"
            venv_python = hub_root / ".venv" / "bin" / "python"
            if venv_python.exists():
                return str(venv_python)
            
            # Check for local development
            hub_core_path = self._find_hub_core_path()
            if hub_core_path:
                venv_path = Path(hub_core_path).parent.parent / ".venv" / "bin" / "python"
                if venv_path.exists():
                    return str(venv_path)
            
            return None
        
        venv_python = find_venv_python()
        python_cmd = venv_python if venv_python else "python3"
        
        # Check for environment variable override
        hub_core_env = os.environ.get("CONTEXT_MESH_HUB_CORE_PATH")
        if hub_core_env and Path(hub_core_env).exists():
            config = {
                "mcpServers": {
                    "context-mesh-hub": {
                        "command": python_cmd,
                        "args": ["-m", "hub_core.server"],
                        "env": {
                            "PYTHONPATH": hub_core_env
                        }
                    }
                }
            }
            # No need for PYTHONPATH if using venv python
            if venv_python:
                del config["mcpServers"]["context-mesh-hub"]["env"]
            return config
        
        # Check for local development setup first (always works)
        hub_core_path = self._find_hub_core_path()
        if hub_core_path:
            config = {
                "mcpServers": {
                    "context-mesh-hub": {
                        "command": python_cmd,
                        "args": ["-m", "hub_core.server"],
                        "env": {
                            "PYTHONPATH": str(hub_core_path)
                        }
                    }
                }
            }
            # No need for PYTHONPATH if using venv python with hub-core installed
            if venv_python:
                del config["mcpServers"]["context-mesh-hub"]["env"]
            return config
        
        # Check if hub_core is installed globally
        try:
            import hub_core
            # Installed via pip/uv
            return {
                "mcpServers": {
                    "context-mesh-hub": {
                        "command": "python3",
                        "args": ["-m", "hub_core.server"]
                    }
                }
            }
        except ImportError:
            pass
        
        # Fallback: use uv run with local path (for when installed via uv tool)
        # Try to find hub-core in common locations
        common_paths = [
            Path.home() / "Jeftar" / "hub" / "hub-core" / "src",
            Path.home() / "projects" / "context-mesh-hub" / "hub-core" / "src",
            Path.home() / "dev" / "context-mesh-hub" / "hub-core" / "src",
        ]
        
        for path in common_paths:
            if path.exists():
                return {
                    "mcpServers": {
                        "context-mesh-hub": {
                            "command": "python3",
                            "args": ["-m", "hub_core.server"],
                            "env": {
                                "PYTHONPATH": str(path)
                            }
                        }
                    }
                }
        
        # Last resort: tell user to set CONTEXT_MESH_HUB_CORE_PATH
        return {
            "mcpServers": {
                "context-mesh-hub": {
                    "command": "python3",
                    "args": ["-m", "hub_core.server"],
                    "env": {
                        "PYTHONPATH": "/path/to/hub-core/src"
                    }
                }
            },
            "_note": "Set CONTEXT_MESH_HUB_CORE_PATH environment variable to your hub-core/src path"
        }

    def get_mcp_config_for_editor(self, editor: str, use_uv: bool = True) -> dict:
        """Get MCP configuration in the format required by the given editor.

        Each editor uses a different top-level key (Cursor/Claude/Gemini: mcpServers;
        VS Code GitHub Copilot: servers). The server entry (command + args) is the same.

        Args:
            editor: One of cursor, copilot, claude, gemini
            use_uv: If True, use uv run when available.
        """
        from hub_cli.config import MCP_EDITORS

        base = self.get_mcp_config(use_uv=use_uv)
        # Strip internal keys
        base = {k: v for k, v in base.items() if not k.startswith("_")}
        # Get the server entry (command + args)
        server_entry = base.get("mcpServers", base.get("servers", {})).get("context-mesh-hub", {})
        if not server_entry:
            return base

        config_key = MCP_EDITORS.get(editor, {}).get("config_key", "mcpServers")
        return {config_key: {"context-mesh-hub": server_entry}}
