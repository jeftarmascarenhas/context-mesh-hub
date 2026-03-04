"""Context Mesh Hub Core - MCP server for context validation and bundling.

Refactored Architecture (v0.2.0):
- Domain Layer: Pure business logic (services/)
- Infrastructure Layer: I/O operations (parsers/, persistence/, scanner/)
- MCP Layer: Thin tool wrappers (mcp/tools/)
"""

__version__ = "0.2.0"

# Main entry point
from .server import create_server, main

# Domain services (for programmatic use)
from .domain.services import (
    IntentService,
    BuildService,
    AnalysisService,
    LearnService,
)

# Infrastructure components
from .loader import ContextLoader
from .validator import ContextValidator
from .bundler import ContextBundler

__all__ = [
    # Entry points
    "create_server",
    "main",
    # Services
    "IntentService",
    "BuildService", 
    "AnalysisService",
    "LearnService",
    # Infrastructure
    "ContextLoader",
    "ContextValidator",
    "ContextBundler",
]
