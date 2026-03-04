---
name: context-mesh
description: Manage Context Mesh documentation framework for AI-First development. Use this skill whenever the user mentions context, features, decisions, intent, build, learn, documentation, or wants to organize project knowledge. ALWAYS use this skill when working in projects with a context/ folder or when the user asks about project structure, feature tracking, decision documentation, brownfield analysis, or the Intent → Build → Learn workflow. Also use when the user wants to initialize a new project for AI-first development, extract context from existing code, or validate their context structure.
---

# Context Mesh Skill

Context Mesh is a **documentation framework** for AI-First development. It's not a database, not an orchestration system—it's **conventions + templates + workflow** that make AI assistants dramatically more effective.

**The Problem**: AI-generated code works, but context disappears. Three months later, your own code looks foreign.

**The Solution**: Context Mesh makes context the primary artifact. Code becomes its manifestation, not the other way around.

---

## Core Workflow: Intent → Build → Learn

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INTENT    │ ──► │    BUILD    │ ──► │    LEARN    │
│  What & Why │     │  AI + Human │     │   Update    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                          ◄────────────────────┘
                              Feedback Loop
```

### Step 1: Intent
**Define what to build and why** before building.

- Create `project-intent.md` for the overall project
- Create `F001-feature-name.md` for each feature
- Create `D001-decision-name.md` for technical decisions
- Document acceptance criteria and constraints

### Step 2: Build
**AI generates code using context**, human supervises.

1. **Plan**: Ask AI to explain what it will build
2. **Approve**: Review and approve the plan
3. **Execute**: AI generates code based on approved plan

**Critical**: Verify a decision (ADR) exists before implementing. If not, create it first.

### Step 3: Learn
**Update context to reflect what changed** and document learnings.

- Update feature status after completion
- Add outcomes to decisions
- Capture patterns and anti-patterns
- Update changelog

---

## Available Tools

The Context Mesh MCP provides 8 consolidated tools. The intelligence is in this Skill—the MCP is just CRUD.

### `cm_init`
**Initialize or migrate context structure**

Use when:
- Starting a new project (`init`)
- Converting existing project to Context Mesh (`existing`)
- Migrating from old context structure (`migrate`)

```
cm_init(operation="init", project_name="my-project")
cm_init(operation="existing", project_path="/path/to/project")
```

### `cm_intent`
**CRUD for features and decisions**

Use when:
- Creating a new feature intent
- Creating a technical decision (ADR)
- Updating feature status
- Listing all features or decisions

Operations: `create`, `update`, `get`, `list`, `delete`
Types: `feature`, `decision`

```
cm_intent(operation="create", type="feature", id="F001", title="User Authentication", ...)
cm_intent(operation="list", type="feature")
cm_intent(operation="update", type="feature", id="F001", status="completed")
```

### `cm_agent`
**Manage agent files**

Use when:
- Creating reusable AI agent instructions
- Updating agent responsibilities
- Listing available agents

```
cm_agent(operation="create", id="A001", name="backend", instructions="...")
cm_agent(operation="list")
```

### `cm_build`
**Bundle context and execute Build Protocol**

Use when:
- Bundling context for AI consumption (`bundle`)
- Starting the Plan → Approve → Execute flow (`plan`, `approve`, `execute`)

```
cm_build(operation="bundle", feature_id="F001")
cm_build(operation="plan", feature_id="F001")
cm_build(operation="approve", plan_id="...")
cm_build(operation="execute", plan_id="...")
```

### `cm_validate`
**Validate context consistency**

Use when:
- Checking if context structure is valid
- Finding broken links between artifacts
- Ensuring status consistency

```
cm_validate()
cm_validate(fix=true)  # Auto-fix simple issues
```

### `cm_analyze`
**Impact analysis and dependency mapping**

Use when:
- Understanding code dependencies
- Analyzing impact of changes
- Brownfield context extraction (see brownfield-guide.md)

Operations: `scan`, `impact`, `dependencies`, `graph`

```
cm_analyze(operation="scan", path="/path/to/project")
cm_analyze(operation="impact", feature_id="F001")
cm_analyze(operation="dependencies", file_path="src/auth/login.py")
```

### `cm_learn`
**Capture and synchronize learnings**

Use when:
- After completing a build cycle
- Capturing what was learned
- Updating context with outcomes

Operations: `initiate`, `review`, `accept`, `apply`

```
cm_learn(operation="initiate", feature_id="F001")
cm_learn(operation="review")
cm_learn(operation="accept", learning_ids=["L001", "L002"])
cm_learn(operation="apply")
```

### `cm_status`
**Get complete context overview**

Use when:
- Understanding current project state
- Getting lifecycle suggestions
- Seeing what to work on next

```
cm_status()
cm_status(verbose=true)
```

---

## Quick Reference

| Task | Tool & Operation |
|------|------------------|
| Start new project | `cm_init(operation="init")` |
| Add existing project | `cm_init(operation="existing")` |
| Create feature | `cm_intent(operation="create", type="feature")` |
| Create decision | `cm_intent(operation="create", type="decision")` |
| List features | `cm_intent(operation="list", type="feature")` |
| Bundle context | `cm_build(operation="bundle")` |
| Start build | `cm_build(operation="plan")` |
| Validate structure | `cm_validate()` |
| Analyze codebase | `cm_analyze(operation="scan")` |
| Capture learnings | `cm_learn(operation="initiate")` |
| Check status | `cm_status()` |

---

## Context Structure

```
context/
├── intent/                    # What & Why
│   ├── project-intent.md      # Overall project intent
│   ├── F001-user-auth.md      # Feature 001
│   ├── F002-payment.md        # Feature 002
│   └── B001-login-error.md    # Bug 001 (optional)
│
├── decisions/                 # How & Trade-offs
│   ├── D001-tech-stack.md
│   ├── D002-auth-approach.md
│   └── D003-database.md
│
├── agents/                    # Reusable AI instructions
│   └── A001-backend.md
│
├── knowledge/                 # Patterns & Anti-patterns
│   ├── patterns/
│   └── anti-patterns/
│
└── evolution/                 # Change tracking
    ├── changelog.md
    └── archived/
```

---

## Reference Guides

For detailed guidance, read these reference files as needed:

### [workflow-guide.md](references/workflow-guide.md)
Read when you need detailed instructions on:
- Intent phase: capturing what/why/acceptance criteria
- Build phase: plan/approve/execute flow
- Learn phase: capturing outcomes, updating context

### [brownfield-guide.md](references/brownfield-guide.md)
Read when working with existing projects:
- How to analyze existing codebases
- Step-by-step brownfield workflow
- Extracting features and decisions from code

### [nomenclature-guide.md](references/nomenclature-guide.md)
Read when creating artifacts:
- F001, D001 naming patterns
- YAML frontmatter templates
- Feature and decision templates

### [parallelization-guide.md](references/parallelization-guide.md)
Read when tasks can be done in parallel:
- Using sub-agents for independent work
- When parallelization helps vs. hurts
- Examples of parallel task execution

---

## Key Principles

1. **Context is primary** — Code is a manifestation of context, not the other way around
2. **Explicit over implicit** — No hidden or inferred critical context
3. **Human decides** — AI proposes, humans approve
4. **Simple prompts** — Reference context files, don't duplicate them
5. **Always validate** — Run `cm_validate()` after making changes

---

## Common Workflows

### New Project
```
1. cm_init(operation="init")
2. Edit project-intent.md
3. cm_intent(operation="create", type="feature", ...) for first feature
4. cm_intent(operation="create", type="decision", ...) for tech stack
5. cm_validate()
```

### Existing Project (Brownfield)
```
1. cm_init(operation="existing")
2. cm_analyze(operation="scan")
3. Review proposed features and decisions
4. Accept and refine incrementally
5. cm_validate()
```

See [brownfield-guide.md](references/brownfield-guide.md) for detailed workflow.

### Building a Feature
```
1. cm_build(operation="bundle", feature_id="F001")
2. cm_build(operation="plan", feature_id="F001")
3. Review plan with user
4. cm_build(operation="approve", plan_id="...")
5. cm_build(operation="execute", plan_id="...")
6. cm_learn(operation="initiate", feature_id="F001")
```

### After Completing Work
```
1. cm_learn(operation="initiate")
2. cm_learn(operation="review")
3. Accept relevant learnings
4. cm_intent(operation="update", ..., status="completed")
5. cm_validate()
```
