# AGENTS.md - Context Mesh Hub

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

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
