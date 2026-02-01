"""MCP server entry point for Hub Core."""

import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .tools import create_tools


def create_server(repo_root: Optional[Path] = None) -> FastMCP:
    """Create and configure the Hub Core MCP server.
    
    Args:
        repo_root: Optional repository root path. Auto-detects if None.
    
    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP("Hub Core")
    
    # Register all tools
    create_tools(mcp, repo_root)
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    import os
    
    # Allow repo root to be passed as command-line argument
    repo_root = None
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()
    else:
        # Try to auto-detect from environment or cwd
        # CONTEXT_MESH_REPO_ROOT env var takes priority
        env_root = os.environ.get("CONTEXT_MESH_REPO_ROOT")
        if env_root:
            repo_root = Path(env_root).resolve()
        else:
            # Use current working directory (set by Cursor to workspace)
            cwd = Path.cwd()
            if (cwd / "context").exists():
                repo_root = cwd
    
    server = create_server(repo_root)
    
    # Run the server in stdio mode (for MCP clients like Cursor)
    # show_banner=False to avoid rich UI when running as MCP server
    server.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
