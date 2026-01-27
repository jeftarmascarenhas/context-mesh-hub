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
    # Allow repo root to be passed as command-line argument
    repo_root = None
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()
    
    server = create_server(repo_root)
    
    # Run the server
    server.run()


if __name__ == "__main__":
    main()
