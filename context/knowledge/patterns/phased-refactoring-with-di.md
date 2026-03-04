# Pattern: Phased Architecture Refactoring with DI

## Context

Large monolithic codebases (5,000+ lines) with code smells require careful refactoring to avoid breaking changes while improving architecture.

During F006-refactor-hub-core-architecture, we successfully refactored hub-core from 5,034 lines (73% problematic) to a clean 3-layer architecture using a phased approach.

## The Pattern

**5-Phase Incremental Refactoring with Dependency Injection**

### Phase 1: Foundation (2 days)
- Create new directory structure (domain/, infrastructure/, mcp/, shared/)
- Extract custom exceptions and configuration
- Move dataclasses to domain/models/
- **Key**: Keep old code working, add new structure in parallel

### Phase 2: Infrastructure (2 days)
- Implement infrastructure layer (parsers, persistence, scanner)
- File-based persistence repositories
- **Key**: New code doesn't touch old code yet

### Phase 3: Domain Services (2 days)
- Extract business logic to pure services
- Implement Dependency Injection (constructor-based)
- Services receive dependencies (no hard-coded imports)
- **Key**: Services are testable in isolation with mocks

### Phase 4: MCP Tools (2 days)
- Split monolithic files into focused thin wrappers
- Each tool <150 lines, delegates to domain services
- Implement error handling decorators
- **Key**: MCP interface stays identical (zero breaking changes)

### Phase 5: Cleanup (1 day)
- Remove legacy files systematically
- Update all imports
- Verify no regressions
- **Key**: Remove only after verifying new code works

## Evidence

**Before:**
- `tools.py`: 2,047 lines (God Object)
- `brownfield.py`: 665 lines (mixed concerns)
- `build_protocol.py`: 446 lines (in-memory state)
- `learn_sync.py`: 515 lines (in-memory state)
- Test coverage: ~10%

**After:**
- 28 new files, largest 645 lines (intent_service.py)
- Clear separation: Domain/Infrastructure/MCP
- File-based persistence (survives restarts)
- Testability: Domain services are pure functions

**Outcome:**
- ✅ Zero breaking changes
- ✅ All tests pass
- ✅ Removed 3,673 lines of problematic code
- ✅ Added ~6,000 lines of structured, maintainable code

## Why It Works

1. **Incremental validation** - Each phase deliverable independently
2. **Parallel implementation** - New code coexists with old until proven
3. **DI enables testing** - Pure services easy to test with mocks
4. **Clear boundaries** - 3-layer architecture prevents coupling creep
5. **File-based persistence** - Simple, sufficient for v1 (no database needed)

## When to Use

Use this pattern when:
- ✅ Codebase >2,000 lines with code smells
- ✅ Need zero breaking changes (production system)
- ✅ Team wants incremental delivery
- ✅ Testing coverage needs dramatic improvement
- ✅ Onboarding time is too high

Don't use when:
- ❌ Codebase <500 lines (overkill)
- ❌ Can afford downtime for rewrite
- ❌ No clear architecture vision

## Implementation Guide

```python
# Example: Domain Service with DI

# domain/services/example_service.py
class ExampleService:
    def __init__(
        self,
        loader: ContextLoader,
        repository: ExampleRepository,
        parser: MarkdownParser
    ):
        # Dependencies injected via constructor
        self.loader = loader
        self.repository = repository
        self.parser = parser
    
    def do_something(self, name: str) -> Result:
        # Pure business logic - no I/O
        data = self.loader.read_artifact(name)
        parsed = self.parser.extract_section(data, "What")
        result = self._business_logic(parsed)
        self.repository.save(result)
        return result

# server.py - DI Setup
def create_server():
    loader = ContextLoader()
    parser = MarkdownParser()
    store = FileStore(Path(".context-mesh"))
    repo = ExampleRepository(store)
    
    service = ExampleService(loader, repo, parser)
    
    # MCP tools receive services
    register_tools(mcp, service)
```

## Anti-Patterns to Avoid

- ❌ **Big Bang Rewrite** - Don't delete old code before new code is proven
- ❌ **Hidden Dependencies** - Don't use singletons or global state
- ❌ **Tight Coupling** - Don't import infrastructure in domain services
- ❌ **No Persistence** - Don't use in-memory state for critical data

## Related

- **Feature**: [F006 - Refactor Hub-Core Architecture](../../intent/F006-refactor-hub-core-architecture.md)
- **Decision**: [D001 - Tech Stack](../../decisions/D001-tech-stack.md) (3-layer architecture rationale)
- **Anti-Pattern**: [Python Relative Imports Pitfall](../anti-patterns/python-relative-imports-pitfall.md)

## Status

- **Created**: 2026-03-04
- **From**: Learn Sync (proposal ed8afea3-4901-4041-a79a-108d2e764259)
- **Confidence**: Medium (first application, needs validation in other projects)
- **Impact**: Low (reusable for similar refactorings)
- **Evidence**: Successful application in hub-core (March 2026)
