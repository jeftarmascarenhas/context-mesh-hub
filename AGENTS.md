# AGENTS.md - Context Mesh Hub

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

---

## 🧠 Context Mesh Framework

This project uses **Context Mesh** for AI-First development.

**Workflow**: Intent → Build → Learn

1. **Intent**: Understand WHAT and WHY before coding
2. **Build**: Implement following decisions, patterns, and governance boundaries
3. **Learn**: Propose and sync learnings into context artifacts (never automatic)

---

## 📌 Product Orientation (Hub)

All execution requests flow through MCP validation.
Direct agent execution without MCP context bundling is invalid.

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
├── intent/ # WHAT to build and WHY (load first)
│ ├── project-intent.md
│ └── feature-.md
├── decisions/ # HOW to build (technical + governance)
│ └── 001-.md
├── knowledge/ # Patterns and anti-patterns
│ ├── patterns/
│ └── anti-patterns/
├── agents/ # Execution agents (DoD-driven)
│ └── agent-*.md
└── evolution/ # Project history
│ └── changelog.md
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


# 🤖 AI Agent Instructions
**Before Any Implementation**
1. Load project intent: `@context/intent/project-intent.md`
2. Load the feature intent you are implementing: `@context/intent/feature-*.md`
3. Load relevant decisions: `@context/decisions/*.md`
4. Load relevant patterns/anti-patterns:
    - @context/knowledge/patterns/*.md
    - @context/knowledge/anti-patterns/*.md

**During Implementation**
1. Execute the correct agent playbook: @context/agents/agent-*.md
2. Respect decisions: technical choices must follow @context/decisions/
3. Follow patterns and avoid anti-patterns
4. Stay within scope: do not expand feature scope without updating context and user approval

**After Implementation**
1. Update the feature intent:
    - mark completed (or partial)
    - add learnings and limitations
2. Update impacted decisions:
    - add outcomes (what worked / what didn’t)
3. Update @context/evolution/changelog.md:
- what changed
- why it changed
- links to feature/decisions

# 📋 Execution Agents
Execution agents are implementers. They produce code changes and must satisfy the Definition of Done.
| Phase | Agent                                           | Purpose                                                              |
| ----: | ----------------------------------------------- | -------------------------------------------------------------------- |
|     1 | `@context/agents/agent-context-bootstrap.md`    | Initialize/validate Context Mesh Hub structure in a repo             |
|     2 | `@context/agents/agent-brownfield-extractor.md` | Extract scoped context from existing codebases (evidence-based)      |
|     3 | `@context/agents/agent-feature-executor.md`     | Implement a specific feature intent end-to-end, bounded by decisions |
|     4 | `@context/agents/agent-learn-sync.md` (optional)| Explicitly formalize learnings and evolution (never automatic)       |



> Notes:
Agents MUST operate within the authority model defined in decisions.
The MCP is the authority gate; agents are operators.

# 📚 Context Files to Load

**Always load (before any work):**
- @context/intent/project-intent.md

**Load per feature:**
- @context/intent/feature-*.md

**Load per phase/execution:**
- @context/agents/agent-*.md
- @context/decisions/*.md
- @context/knowledge/patterns/*.md
- @context/knowledge/anti-patterns/*.md

# ✅ Definition of Done (Build Phase)

The Definition of Done is specified inside each `@context/agents/agent-*.md`.

General checklist:
- All Acceptance Criteria in the feature intent are met (or explicitly marked partial with reasons)
- Code follows applicable patterns
- No anti-patterns introduced
- Build passes without errors
- Tests pass (if applicable)
- Scope matches approved Build plan (no silent scope expansion)
- Context updated (Intent / Decisions / Changelog)

# ⚠️ AI Agent Rules
✅ ALWAYS
- Load context files before implementing
- Follow decisions from @context/decisions/
- Use patterns from @context/knowledge/patterns/
- Update context after implementation
- Check the DoD before completing a phase
- Provide explicit boundaries (what you changed, where, and why)
❌ NEVER
- Ignore documented decisions
- Use anti-patterns from @context/knowledge/anti-patterns/
- Leave context stale after implementation
- Skip loading intent files
- Implement without understanding the WHY
- Assume authority: agents propose; humans approve

# 📝 File Creation Rules (CRITICAL)

**When to CREATE files:**

✅ User explicitly asks to create/implement/add something

✅ User uses prompts like "add feature", "fix bug", "implement"

✅ Following a Context Mesh prompt (add-feature.md, fix-bug.md, etc.)

✅ An execution agent requires specific files as part of its DoD

**When to NOT create files (Questions/Explanations):**

❌ User asks a question or wants clarification

❌ User is exploring options or learning about the codebase

❌ User asks for suggestions/recommendations only

**When user asks questions:**

1. Answer using @context/ files
2. DO NOT create markdown files automatically
3. You MAY suggest updates, but do not apply them without request

# 🔄 Context Update (Critical)

**After completing any feature:**
1. Update @context/intent/feature-*.md
   - mark status
   - add learnings
2. Update @context/decisions/*.md
   - add outcomes
   - document what worked/didn't
3. Update @context/evolution/changelog.md
   - what changed
   - why it changed
Never leave context stale. Future AI sessions depend on accurate context.

# 🎨 Code Style
- TypeScript strict mode (where applicable)
- Keep changes minimal and scoped
- Prefer explicitness over cleverness
- Follow patterns from @context/knowledge/patterns/
