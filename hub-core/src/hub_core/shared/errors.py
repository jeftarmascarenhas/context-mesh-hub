"""Custom exceptions for Context Mesh Hub Core.

Provides consistent error handling across all layers.
"""


class ContextMeshError(Exception):
    """Base exception for all Context Mesh Hub errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dict format for MCP responses."""
        return {
            "error": self.message,
            "error_type": self.__class__.__name__,
            "details": self.details,
        }


class ArtifactNotFoundError(ContextMeshError):
    """Raised when a context artifact (feature, decision, etc.) is not found."""
    
    def __init__(self, artifact_type: str, identifier: str):
        super().__init__(
            f"{artifact_type} not found: {identifier}",
            {"artifact_type": artifact_type, "identifier": identifier}
        )


class ValidationError(ContextMeshError):
    """Raised when validation fails (context structure, content, etc.)."""
    
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, {"validation_errors": errors or []})


class PersistenceError(ContextMeshError):
    """Raised when file I/O operations fail (save, load, etc.)."""
    
    def __init__(self, operation: str, path: str, reason: str):
        super().__init__(
            f"Persistence error during {operation}: {reason}",
            {"operation": operation, "path": path, "reason": reason}
        )


class InvalidOperationError(ContextMeshError):
    """Raised when an operation is invalid in current state."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Invalid operation '{operation}': {reason}",
            {"operation": operation, "reason": reason}
        )


class PlanNotApprovedError(ContextMeshError):
    """Raised when attempting to execute a plan that hasn't been approved."""
    
    def __init__(self, plan_id: str, current_status: str):
        super().__init__(
            f"Plan {plan_id} is not approved (current status: {current_status})",
            {"plan_id": plan_id, "current_status": current_status}
        )


class ContextNotInitializedError(ContextMeshError):
    """Raised when Context Mesh structure doesn't exist in repository."""
    
    def __init__(self, repo_root: str):
        super().__init__(
            f"Context Mesh not initialized in {repo_root}",
            {"repo_root": repo_root, "hint": "Use cm_init(action='new') to initialize"}
        )
