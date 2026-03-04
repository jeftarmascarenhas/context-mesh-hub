# Anti-Pattern: Python Relative Import Path Confusion

## Context

During implementation of F006-refactor-hub-core-architecture, systematic errors occurred due to confusion between relative import path syntax in deeply nested Python module structures.

## The Problem

When refactoring into a 3-layer architecture with structure:
```
hub_core/
├── domain/
├── infrastructure/
├── mcp/
│   └── tools/  # Tools are 2 levels deep
└── shared/
```

Tools in `mcp/tools/*.py` need to import from `shared/`, `domain/`, etc.

**Wrong approach tried initially:**
```python
# In mcp/tools/cm_init.py
from ..shared.errors import ContextMeshError  # ❌ Only goes up 1 level to mcp/
from .decorators import handle_mcp_errors      # ❌ Looks in mcp/tools/ (wrong)
```

**Correct approach:**
```python
# In mcp/tools/cm_init.py
from ...shared.errors import ContextMeshError  # ✅ Goes up 2 levels to hub_core/
from ..decorators import handle_mcp_errors     # ✅ Goes up 1 level to mcp/
```

## Evidence

- All 8 files in `mcp/tools/*.py` required import path fixes
- Systematic pattern: needed `...` (3 dots) to reach hub_core root
- Caused Pylance errors initially, required manual verification

Files affected:
- `mcp/tools/cm_init.py`
- `mcp/tools/cm_intent.py`
- `mcp/tools/cm_agent.py`
- `mcp/tools/cm_analyze.py`
- `mcp/tools/cm_build.py`
- `mcp/tools/cm_learn.py`
- `mcp/tools/cm_validate.py`
- `mcp/tools/cm_status.py`

## Why It Happens

- Python relative imports use `.` for "current package", `..` for "one level up", `...` for "two levels up"
- Easy to lose count when structure is deeply nested
- IDEs don't always catch this immediately (depends on environment configuration)

## Recommendation

**When creating nested module structures:**

1. **Draw the tree first** - visualize depth before writing imports
2. **Count the dots** - explicitly count how many levels up you need to go
3. **Test imports early** - verify import paths work before implementing logic
4. **Use absolute imports** - when in doubt, use absolute imports from package root:
   ```python
   from hub_core.shared.errors import ContextMeshError
   ```

**Pattern for nested tool files:**
```python
# Rule: mcp/tools/*.py files are 2 levels deep
from ...domain.services import SomeService    # 3 dots to root
from ...shared.errors import ContextMeshError # 3 dots to root
from ..decorators import handle_mcp_errors    # 2 dots to mcp/
```

## Related

- **Feature**: [F006 - Refactor Hub-Core Architecture](../../intent/F006-refactor-hub-core-architecture.md)
- **Decision**: [D001 - Tech Stack](../../decisions/D001-tech-stack.md)

## Status

- **Created**: 2026-03-04
- **From**: Learn Sync (proposal ed8afea3-4901-4041-a79a-108d2e764259)
- **Confidence**: High
- **Impact**: Medium
