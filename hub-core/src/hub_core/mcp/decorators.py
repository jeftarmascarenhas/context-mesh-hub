"""MCP decorators for error handling and common functionality."""

from functools import wraps
from typing import Any, Callable, Dict

from ..shared.errors import ContextMeshError


def handle_mcp_errors(func: Callable) -> Callable:
    """Decorator to handle MCP tool errors consistently.
    
    Converts exceptions into MCP-friendly error responses.
    
    Args:
        func: MCP tool function to wrap
    
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except ContextMeshError as e:
            # Convert custom exceptions to dict
            return e.to_dict()
        except Exception as e:
            # Catch-all for unexpected errors
            return {
                "error": f"Internal error: {str(e)}",
                "type": "InternalError",
            }
    return wrapper
