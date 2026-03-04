# Parallelization Guide: Using Sub-Agents for Independent Tasks

This guide explains when and how to use sub-agents for parallel task execution in Context Mesh workflows.

---

## When to Parallelize

### Good Candidates for Parallelization

Tasks are good for parallelization when they are:

1. **Independent** — No dependencies between them
2. **Well-defined** — Clear inputs and outputs
3. **Self-contained** — Don't need results from other tasks

### Examples of Parallelizable Work

| Scenario | Parallel Tasks |
|----------|----------------|
| Multi-layer changes | Backend API + Frontend UI + Database migration |
| Documentation | Update README + Update API docs + Update changelog |
| Multi-feature | Feature A implementation + Feature B implementation |
| Code + Context | Write code + Update context files |
| Testing | Unit tests + Integration tests + E2E tests |

### When NOT to Parallelize

Avoid parallel execution when:

- Tasks depend on each other's output
- Order matters (e.g., migration before code)
- Tasks modify the same files
- You need to review before proceeding
- The task is small enough to do sequentially

---

## Parallelization Patterns

### Pattern 1: Layer Parallelization

When making changes across architectural layers:

```
┌─────────────────────────────────────────────┐
│              Main Agent                      │
│  Coordinates and reviews                     │
└─────────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Sub-Agent │  │ Sub-Agent │  │ Sub-Agent │
│  Backend  │  │ Frontend  │  │ Database  │
│  API      │  │   UI      │  │ Migration │
└───────────┘  └───────────┘  └───────────┘
```

**Example prompt:**
```
Implement F001 User Authentication.

Execute in parallel:
1. Backend: Create API endpoints following D001
2. Frontend: Create login form following design spec
3. Database: Create migration for users table

Wait for all to complete, then integrate.
```

### Pattern 2: Documentation Parallelization

When updating multiple docs:

```
┌─────────────────────────────────────────────┐
│              Main Agent                      │
│  Gathers context, distributes tasks          │
└─────────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Sub-Agent │  │ Sub-Agent │  │ Sub-Agent │
│  README   │  │ API Docs  │  │ Changelog │
└───────────┘  └───────────┘  └───────────┘
```

### Pattern 3: Analysis Parallelization

When analyzing a large codebase:

```
┌─────────────────────────────────────────────┐
│              Main Agent                      │
│  Defines slices, aggregates results          │
└─────────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Sub-Agent │  │ Sub-Agent │  │ Sub-Agent │
│  src/auth │  │src/payment│  │ src/api   │
└───────────┘  └───────────┘  └───────────┘
```

---

## How to Use Sub-Agents

### Spawning Sub-Agents

When you identify independent tasks, spawn sub-agents:

```
Execute the following tasks in parallel:

Task 1 - Backend API:
- Create /api/auth/login endpoint
- Create /api/auth/register endpoint
- Follow patterns in D001-auth-strategy.md

Task 2 - Frontend UI:
- Create LoginForm component
- Create RegisterForm component
- Follow design system patterns

Task 3 - Tests:
- Write unit tests for auth module
- Write integration tests for auth endpoints
```

### Context for Sub-Agents

Each sub-agent should receive:

1. **Specific task** — Clear scope of what to do
2. **Relevant context** — Only the files they need
3. **Constraints** — Patterns to follow, anti-patterns to avoid
4. **Output location** — Where to save results

### Collecting Results

After parallel execution:

1. Review each sub-agent's output
2. Check for conflicts or inconsistencies
3. Integrate changes
4. Run validation

---

## Real Example: MCP Simplification

This project used parallelization for Stream A + Stream B:

```
┌─────────────────────────────────────────────┐
│              Main Coordination               │
│  D013 decision, overall architecture         │
└─────────────────────────────────────────────┘
        │                        │
        ▼                        ▼
┌───────────────────┐  ┌───────────────────┐
│    Stream A       │  │    Stream B       │
│  MCP Tools        │  │  Context Mesh     │
│  8 consolidated   │  │  Skill            │
│  tools            │  │                   │
└───────────────────┘  └───────────────────┘
```

**Why this worked:**
- Stream A (MCP) and Stream B (Skill) are independent
- Different file locations, no conflicts
- Both follow the same D013 decision
- Can be developed and tested separately

---

## Guidelines

### Do
- ✅ Use parallelization for truly independent tasks
- ✅ Give each sub-agent clear, focused scope
- ✅ Review and integrate results carefully
- ✅ Run validation after parallel work completes

### Don't
- ❌ Parallelize dependent tasks
- ❌ Have multiple agents modify the same file
- ❌ Skip the review/integration step
- ❌ Use parallelization for small, quick tasks

---

## Parallelization Checklist

Before parallelizing, verify:

- [ ] Tasks are truly independent
- [ ] No shared file modifications
- [ ] Each task has clear scope
- [ ] Context is properly distributed
- [ ] Integration plan exists
- [ ] Validation will run after

---

## When Sequential is Better

Sometimes sequential execution is better:

| Situation | Why Sequential |
|-----------|----------------|
| Learning workflow | Need to understand output before next step |
| Dependent features | Feature B needs Feature A |
| Same file changes | Avoid merge conflicts |
| Critical path | Need human review at each step |
| Small tasks | Overhead isn't worth it |

**Rule of thumb**: If you're unsure, start sequential. Parallelize when you see clear opportunities.

---

## Summary

Parallelization is **optional** but powerful when used correctly:

1. Identify independent tasks
2. Spawn sub-agents with clear scope
3. Give each agent relevant context only
4. Review and integrate results
5. Validate the combined output

The Context Mesh workflow (Intent → Build → Learn) is inherently sequential, but **within each phase**, you can parallelize independent work.
