"""MCP Client for connecting to Context Mesh Hub server."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel


class MCPToolResult(BaseModel):
    """Result from an MCP tool call."""
    
    success: bool
    content: Any
    error: Optional[str] = None


class MCPClient:
    """Client for interacting with the Context Mesh Hub MCP server.
    
    This client can operate in two modes:
    1. Direct mode: Import and call hub_core directly (for local development)
    2. Subprocess mode: Spawn the MCP server and communicate via stdio
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the MCP client.
        
        Args:
            repo_root: Path to the repository root. If None, uses current directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self._server_process: Optional[subprocess.Popen] = None
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any] = None) -> MCPToolResult:
        """Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call (e.g., 'cm_help', 'cm_add_feature')
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPToolResult with the tool's response
        """
        arguments = arguments or {}
        
        try:
            # Try direct import first (for development)
            return await self._call_tool_direct(tool_name, arguments)
        except ImportError:
            # Fall back to subprocess mode
            return await self._call_tool_subprocess(tool_name, arguments)
    
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
        # Check multiple locations
        candidates = [
            self.repo_root / "hub-core",  # Same level (inside hub/)
            self.repo_root.parent / "hub-core",  # Parent level (sibling)
            Path.home() / "Jeftar" / "hub" / "hub-core",  # Known location
        ]
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
        
        # Create server instance
        server = create_server(self.repo_root)
        
        # Find and call the tool
        # Tools are registered on the server, we need to find the right one
        for tool in server._tool_manager._tools.values():
            if tool.name == tool_name:
                # Call the tool function
                result = await tool.fn(**arguments) if asyncio.iscoroutinefunction(tool.fn) else tool.fn(**arguments)
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
