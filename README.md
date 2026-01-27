# Context Mesh Hub (context-mesh-hub)

**Context is Primary. Code is Manifestation.**

Context Mesh Hub is a **local-first, repo-first, MCP-first** system that turns AI-assisted development into a **governed, repeatable process**.

It standardizes how teams create, validate, execute, and evolve **context artifacts** so any AI agent (Cursor, Copilot, Claude, etc.) can operate safely and consistently.

---

## Why

AI coding without governance creates:
- hidden assumptions
- silent scope creep
- inconsistent outcomes
- untraceable evolution
- brittle codebases

Context Mesh Hub solves this by making **context explicit, versioned, and enforceable**.

---

## What It Is

A local system that:
- **visualizes** and validates Context Mesh artifacts (`context/`)
- provides a **Build Protocol** inside the Build phase: **Plan → Approve → Execute**
- supports **brownfield extraction** (evidence-based context from legacy repos)
- enables **explicit learning** and **controlled evolution**

---

## v1 Constraints

- Repo-first (no database)
- UI runs locally (Next.js)
- MCP is the authority gate for actions
- Agents are operators, never authorities

---

## Core Workflow (Context Mesh)

**Intent → Build → Learn**

1) **Intent**: define WHAT and WHY (feature intents + acceptance criteria)  
2) **Build**: execute with governance boundaries (decisions + patterns)  
3) **Learn**: formalize outcomes into reusable knowledge and evolution logs

---

## Repository Structure

```txt
context/
├── intent/
│   ├── project-intent.md
│   └── feature-*.md
├── decisions/
│   └── 001-*.md
├── knowledge/
│   ├── patterns/
│   └── anti-patterns/
├── agents/
│   └── agent-*.md
└── evolution/
    └── changelog.md
```

# How Agents Work Here

**Agents (Cursor/Copilot/Claude/etc.) must follow:**

- AGENTS.md (operational contract)

- context/.context-mesh-framework.md (kernel rules)

- execution playbooks in context/agents/

**Execution agents**

- agent-context-bootstrap.md

- agent-brownfield-extractor.md

- agent-feature-executor.md

- agent-learn-sync.md (explicit, never automatic)

# Quick Start
```bash
pnpm install
pnpm dev
pnpm test
pnpm build
```

# Build Protocol

Inside Build, execution is gated:

1. Plan — generate an explicit execution plan

2. Approve — human validates plan and boundaries

3. Execute — agent implements only what was approved

No implicit scope expansion.
No silent evolution.

# Brownfield (Legacy Repos)

**Context Mesh Hub can enter large codebases safely by:**

- mapping repository surfaces

- extracting observable behaviors

- tagging constraints and risks

- generating draft context artifacts with evidence

No refactors. No invented intent.

# License

Open source (TBD).

## References

Context Mesh Framework: https://github.com/jeftarmascarenhas/context-mesh
AGENTS.md standard: https://agents.md/


---

## 3) Build Phase — passo a passo com execution flow (Context Mesh Hub)

Abaixo um fluxo “copy/paste mental” que você pode colocar no README depois como **Build Playbook**.

### Execution Flow (Hub v1)

1. **Load Context Bundle (MCP)**
   - Load:
     - `@context/.context-mesh-framework.md`
     - `@context/intent/project-intent.md`
     - target `@context/intent/feature-*.md`
     - relevant `@context/decisions/*.md`
     - patterns/anti-patterns if referenced  
   ↓

2. **Execute Agent 1: Context Bootstrap**
   - `@context/agents/agent-context-bootstrap.md`  
   → **Verify** (structure + required files)  
   → **Approve** (human confirms repo is compliant)  
   ↓

3. **(Optional, Brownfield Only) Execute Agent 2: Brownfield Extractor**
   - `@context/agents/agent-brownfield-extractor.md`  
   → **Verify** (evidence-based report + DRAFT artifacts)  
   → **Approve** (human accepts/rejects drafts into context)  
   ↓

4. **Execute Agent 3: Feature Executor (Mode: Plan)**
   - `@context/agents/agent-feature-executor.md` in **Plan** mode  
   → Output: plan, affected files, risks, assumptions  
   → **Verify** (plan maps to Acceptance Criteria)  
   → **Approve** (human approves plan boundaries)  
   ↓

5. **Execute Agent 3: Feature Executor (Mode: Execute)**
   - `@context/agents/agent-feature-executor.md` in **Execute** mode  
   → Implement only approved scope  
   → **Verify** (build/tests/manual check)  
   → **Approve** (human validates Acceptance Criteria met)  
   ↓

6. **Execute Agent 4: Learn Sync (Explicit)**
   - `@context/agents/agent-learn-sync.md`  
   → Propose learning artifacts (taxonomy-driven)  
   → Propose changelog update  
   → **Verify** (evidence + confidence + impact)  
   → **Approve** (human accepts updates to context artifacts)  
   ↓

7. **Final Validation**
   - Full app run / smoke test (as applicable)
   - Confirm context is not stale:
     - feature marked complete/partial
     - decisions outcomes updated
     - changelog updated

---

### Optional “Enterprise Extensions” (v2+)

- **Agent: Testing** (mandatory in enterprise repos)
  → Verify → Approve  
- **Agent: CI/CD** (pipeline scaffolding)
  → Verify → Approve  
- **Agent: Security / Compliance** (policy scanning)
  → Verify → Approve  

---

