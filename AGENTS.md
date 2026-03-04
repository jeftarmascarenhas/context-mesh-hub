# AGENTS.md - Context Mesh Hub

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

---

## 📖 Artifact Specifications

**CRITICAL**: Before creating or updating any Context Mesh artifact, load the specifications:

📋 **Load**: `@context/knowledge/ARTIFACT_SPECS.md`

This file defines:
- ✅ Required sections for each artifact type (Feature, Decision, Pattern, etc.)
- ⚠️ Recommended sections
- ❌ Optional sections
- 📝 Naming conventions (`F00X-*.md`, `D00X-*.md`)
- 🔗 Cross-reference rules
- ✅ Validation rules

**Never create artifacts from scratch without consulting ARTIFACT_SPECS.md first.**

---

## 🧠 Context Mesh Framework

This project uses [Context Mesh](https://github.com/jeftarmascarenhas/context-mesh) for AI-First development.

**Workflow**: Intent → Build → Learn

1. **Intent** (Step 1): Understand WHAT and WHY before coding
2. **Build** (Step 2): Implement following decisions, patterns, and governance boundaries
3. **Learn** (Step 3): Propose and sync learnings into context artifacts (never automatic)

---

## 📌 Product Orientation (Hub)

All execution requests flow through MCP validation.
Direct agent execution without MCP context bundling is invalid.

When the user asks to **implement**, **execute**, or **write** something, the agent MUST use Context Mesh MCP (build, verify, gate check) when the project has Context Mesh configured and MCP is available — see [When the user asks to implement, execute, or write something](#when-the-user-asks-to-implement-execute-or-write-something).

Context Mesh Hub is a **local-first, repo-first, MCP-first** system that:
- visualizes and validates context artifacts (`context/`)
- provides governance for AI-assisted work (Plan → Approve → Execute inside Build)
- supports brownfield extraction (evidence-based)
- enables explicit learning and evolution (Learn Sync)

**v1 constraints**
- Repo-first (no database)
- UI is local (Next.js)
- MCP is the single authority gate for actions
- Agents are operators, never authorities

---

## 📂 Context Structure

```
context/
├── intent/           # WHAT to build and WHY (load first)
│   ├── project-intent.md      # Project vision and goals
│   └── feature-*.md           # Feature requirements + Acceptance Criteria
├── decisions/        # HOW to build (technical + governance)
│   └── 001-*.md               # Decisions with rationale
├── knowledge/        # Patterns and anti-patterns
│   ├── patterns/              # Code patterns to FOLLOW
│   └── anti-patterns/         # What to AVOID
├── agents/           # Execution agents for each phase
│   └── agent-*.md             # Step-by-step instructions + Definition of Done
└── evolution/        # Project history
    └── changelog.md           # What changed and why
```

---

## 🚀 Quick Start

> Adapt as implementation progresses. Default expectations for v1:

```bash
pnpm install
pnpm dev
pnpm test
pnpm build
```


## 🤖 AI Agent Instructions
### Before Any Implementation

1. **Load project intent**: `@context/intent/project-intent.md`
2. **Load feature intent**: `@context/intent/feature-*.md` (for the feature you're implementing)
3. **Load decisions**: `@context/decisions/*.md` (relevant to the feature)
4. **Load patterns**: `@context/knowledge/patterns/*.md`
5. **Load anti-patterns**: `@context/knowledge/anti-patterns/*.md`

### During Implementation

1. **Execute the agent**: `@context/agents/agent-*.md` for the current phase
2. **Follow patterns**: Use patterns from `@context/knowledge/patterns/`
3. **Avoid anti-patterns**: Check `@context/knowledge/anti-patterns/`
4. **Respect decisions**: All technical choices are documented in `@context/decisions/`
5. **Stay within scope**: Do not expand feature scope without updating context and user approval

### After Implementation
1. **Mark feature as completed** in the intent file
2. **Add outcomes** to decision files (what worked, what didn’t)
3. **Update changelog.md** with what changed

## 📋 Execution Agents

Execute phases in order. Each agent has its own **Definition of Done**.

Execution agents are implementers. They produce code changes and must satisfy the Definition of Done.

| Phase | Agent | Purpose |
|-------|-------|---------|
| 1 | `@context/agents/agent-context-bootstrap.md` | Initialize/validate Context Mesh Hub structure in a repo |
| 2 | `@context/agents/agent-brownfield-extractor.md` | Extract scoped context from existing codebases (evidence-based) |
| 3 | `@context/agents/agent-feature-executor.md` | Implement a specific feature intent end-to-end, bounded by decisions |
| 4 | `@context/agents/agent-learn-sync.md` (optional) | Explicitly formalize learnings and evolution (never automatic) |

> **Notes:**
> - Agents MUST operate within the authority model defined in decisions.
> - The MCP is the authority gate; agents are operators.

## 📚 Context Files to Load

**Always load (before any work):**
- `@context/intent/project-intent.md` - Project vision and constraints

**Load per feature:**
- `@context/intent/feature-*.md` - Feature requirements (has Acceptance Criteria)

**Load per phase:**
- `@context/agents/agent-*.md` - Execution steps (has Definition of Done)
- `@context/decisions/*.md` - Technical decisions
- `@context/knowledge/patterns/*.md` - Patterns to follow
- `@context/knowledge/anti-patterns/*.md` - What to avoid

## ✅ Definition of Done (Technical/Build Phase)

Definition of Done is defined in each **agent file** (`agent-*.md`).

General checklist:
- [ ] All Acceptance Criteria in the feature intent are met (or explicitly marked partial with reasons)
- [ ] Code follows patterns from `@context/knowledge/patterns/`
- [ ] No anti-patterns introduced
- [ ] Build passes without errors
- [ ] Tests pass (if applicable)
- [ ] Scope matches approved Build plan (no silent scope expansion)
- [ ] Context updated (Intent / Decisions / Changelog)

## ⚠️ AI Agent Rules

### ✅ ALWAYS
- Load context files before implementing
- Follow decisions from `@context/decisions/`
- Use patterns from `@context/knowledge/patterns/`
- Update context after implementation
- Check Definition of Done before completing a phase
- Provide explicit boundaries (what you changed, where, and why)

### ❌ NEVER
- Ignore documented decisions
- Use patterns from `@context/knowledge/anti-patterns/`
- Leave context stale after implementation
- Skip loading intent files
- Implement without understanding the WHY
- Assume authority: agents propose; humans approve

### 📝 File Creation Rules (CRITICAL)

**When to CREATE files:**
- ✅ User explicitly asks to create/implement/add something
- ✅ User uses prompts like "add feature", "fix bug", "implement"
- ✅ User explicitly requests: "create", "make", "build", "generate"
- ✅ Following a Context Mesh prompt (add-feature.md, fix-bug.md, etc.)
- ✅ An execution agent requires specific files as part of its DoD

**When to NOT create files (Questions/Explanations):**
- ❌ User asks a question (e.g., "How does X work?", "What is Y?", "Why did we choose Z?")
- ❌ User asks for explanation or clarification
- ❌ User asks "What should I do?" or "What's the best approach?"
- ❌ User is exploring or learning about the codebase
- ❌ User asks for suggestions or recommendations

**When user asks questions:**
1. **Answer the question** using context from `@context/` files
2. **DO NOT create any markdown files** automatically
3. **You CAN suggest** updating Context Mesh if relevant, but:
   - Use format: "💡 **Suggestion**: Consider updating `@context/decisions/001-tech-stack.md` with this information..."
   - **DO NOT create the file** - just suggest it
   - Let the user decide if they want to update

**Examples:**

❌ **WRONG** (User asks question):
```
User: "How does authentication work in this project?"
AI: [Creates feature-auth.md automatically] ❌ DON'T DO THIS
```

✅ **CORRECT** (User asks question):
```
User: "How does authentication work in this project?"
AI: "Based on @context/decisions/002-auth-approach.md, we use JWT tokens...
     💡 **Suggestion**: If this information is outdated, consider updating 
     the decision file with current implementation details."
```

✅ **CORRECT** (User explicitly requests):
```
User: "Add a new feature for user profiles"
AI: [Creates feature-user-profiles.md and decision] ✅ CORRECT
```

## 🔄 Context Update (Critical)

After completing any feature:

```markdown
1. Update @context/intent/feature-*.md
   - Mark as completed
   - Add any learnings

2. Update @context/decisions/*.md
   - Add outcomes section
   - Document what worked/didn't

3. Update @context/evolution/changelog.md
   - What changed
   - Why it changed
```

**Never leave context stale. Future AI sessions depend on accurate context.**

## 🔌 MCP and Living Context

### When the user asks to implement, execute, or write something

In **any project that has Context Mesh configured** (e.g. has a `context/` directory and this AGENTS.md or project intent references Context Mesh, or the Context Mesh Hub MCP server is connected to the agent):

- **Treat implement/execute/write requests as governed by Context Mesh.** Do not go straight to writing code without involving context and, when available, MCP.
- **When Context Mesh Hub MCP is available:**
  1. **Before** implementing: use MCP to check state and gates — e.g. `cm_lifecycle_state`, `cm_gate_check("intent-to-build", feature_name)`, `context_validate`, `cm_status`. If the user did not name a feature, use `cm_suggest_next` or list features and align on one.
  2. **Plan:** If there is no approved plan yet, use `build_plan(feature_name)` (or suggest creating intent first with `cm_add_feature`), then get user approval before executing.
  3. **Execute** only after an approved plan (and gate checks pass where required). Prefer `build_execute(plan_id)` when the workflow provides it; otherwise implement within the scope of the approved plan and context.
  4. **After** implementing: verify with `context_validate` or `cm_status`; optionally run `cm_gate_check("build-to-learn", feature_name)` and then `learn_sync_initiate` to capture learnings.
- **When MCP is not available:** Still follow the workflow: load context files (`@context/intent/`, `@context/decisions/`, `@context/agents/`), produce a plan in conversation, get explicit approval, then implement and update context (intent, decisions, changelog) afterward.

This ensures that in Context Mesh–configured projects, **implement / execute / write** always go through context and, when possible, through MCP build, verify, and gate checks.

---

**Can the agent call MCP when the user asks for implementation out of context or not linked to context?**

**Yes.** The agent can and should use MCP to learn, build, verify, and document — whether the work was governed (from a feature intent + plan) or ad-hoc (user asked for something not yet in context).

### When implementation is *not* linked to context (ad-hoc)

1. **Build (plan first)**  
   - `build_plan(feature_name)` requires an existing feature in context. If the user asks to "implement login" and there is no feature intent:
   - **Option A (governed):** Suggest creating context first: call `cm_add_feature` (and `cm_create_decision` if needed), then `build_plan(feature_name)`.
   - **Option B (ad-hoc then document):** Implement what the user asked, then use MCP to bring it into context (see "Ensure living context" below).

2. **Verify**  
   - Always available: `context_validate`, `cm_status`, `cm_gate_check`, `cm_lifecycle_state`. Use these to check context health and gates regardless of whether the last change was from a plan or ad-hoc.

3. **Learn / document after the fact**  
   - To ensure **living context** after ad-hoc implementation:
     1. **Document intent:** Call `cm_add_feature` with name, what, why, acceptance criteria for what was built (retroactive feature).
     2. **Document decision (if applicable):** Call `cm_create_decision` for the technical approach used.
     3. **Sync learnings:** Call `learn_sync_initiate(feature_name, user_feedback="...")` with the same feature name used in step 1 to capture outcomes and propose changelog/updates.
     4. **Verify:** Call `context_validate` or `cm_status` to confirm context is consistent.

### When to use MCP regardless of link to context

| Goal | MCP tools to use |
|------|-------------------|
| **Verify** context integrity | `context_validate`, `cm_status`, `cm_gate_check` |
| **Learn** after any implementation | `learn_sync_initiate` (after feature exists or was just added), `learn_sync_review`, `learn_sync_apply` |
| **Document** ad-hoc work | `cm_add_feature`, `cm_create_decision`, then `learn_sync_initiate` |
| **Check** lifecycle / next step | `cm_lifecycle_state`, `cm_suggest_next`, `cm_workflow_guide` |

Agents are **operators, not authorities** (Decision 007). MCP does not block calls when work is "out of context"; it provides tools to **bring work into context** and **keep context living**. Use MCP to verify and to ensure living context after any implementation the user requested.

## 🎨 Code Style

> [Adapt to your project]

- TypeScript strict mode (where applicable)
- Keep changes minimal and scoped
- Prefer explicitness over cleverness
- Follow patterns from `@context/knowledge/patterns/`

---

## 📖 References

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)
- [AGENTS.md Standard](https://agents.md/)
