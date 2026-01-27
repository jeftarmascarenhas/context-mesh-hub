# Agent: Context Bootstrap — Context Mesh Hub

## Purpose

Initialize and validate the repository for **Context Mesh Hub** operation.

This agent ensures the repository is **Context Mesh compliant**:
- required context structure exists
- foundational governance files exist
- links and conventions are consistent
- the project is ready for Brownfield extraction and Feature execution

This agent does **not** implement product features.

---

## Context Files to Load

- @context/.context-mesh-framework.md
- @context/intent/project-intent.md
- @context/decisions/001-tech-stack.md
- @context/decisions/003-context-bundling-strategy.md
- @context/decisions/004-build-execution-modes.md
- @context/decisions/005-brownfield-context-extraction.md
- @context/decisions/006-ui-readonly-by-default.md
- @context/decisions/007-agent-scope-and-authority.md
- @context/decisions/008-learning-artifact-taxonomy.md
- @context/decisions/009-context-evolution-rules.md
- @context/evolution/changelog.md (if exists)

---

## Scope

### Allowed
- Create missing Context Mesh scaffolding under `context/`
- Create or update **only** structural files and placeholders required for compliance
- Create minimal `.env.example` / tooling placeholders if referenced by decisions (optional)

### Prohibited
- Do not implement product features
- Do not modify application source code (except minimal scaffolding if repo is empty)
- Do not infer new decisions or intents
- Do not execute refactors
- Do not add dependencies unless explicitly required by existing decisions

---

## Execution Steps

### 1) Validate Repository Context Mesh Structure

Ensure the following directories exist (create if missing):

```
context/
├── intent/
├── decisions/
├── knowledge/
│ └── patterns/
│ └── anti-patterns/
├── agents/
├── evolution/
```


### 2) Validate Required Core Files

Ensure the following files exist (create placeholders if missing, without inventing content):

- `context/.context-mesh-framework.md`
- `context/intent/project-intent.md`
- `context/evolution/changelog.md`

If any file is missing:
- create it as a placeholder with a clear TODO header
- do not fabricate requirements or decisions

### 3) Validate Decision Index and Naming Conventions

- Validate decisions follow: `context/decisions/NNN-*.md`
- Validate no duplicate numbers
- Validate links referenced by feature intents resolve correctly

If inconsistencies exist:
- propose fixes (rename/link updates)
- do not apply destructive renames without explicit user approval

### 4) Validate Feature Inventory

- List all files in `context/intent/feature-*.md`
- Ensure each feature has:
  - What / Why / Scope / Acceptance Criteria
  - Related links to Project Intent + relevant decisions (at minimum 001 and any governance decisions)

If a feature is missing required sections:
- propose a patch list
- do not rewrite feature content unless the user requests it

### 5) Validate Agent Inventory

- List all files in `context/agents/agent-*.md`
- Ensure `AGENTS.md` exists at repository root
- Ensure AGENTS.md references:
  - Context Mesh workflow
  - context structure
  - Definition of Done principle
  - file creation rules
  - authority model (agents are operators)

If `AGENTS.md` is missing:
- create it using the repository standard
If present but inconsistent:
- propose updates

### 6) Validate Evolution Logging

- Ensure `context/evolution/changelog.md` exists
- Ensure the changelog supports:
  - date
  - what changed
  - why
  - references to intents/decisions

Add a single bootstrap entry if file exists but has no entries:
- “Initialized Context Mesh Hub context scaffolding”

### 7) Bootstrap Knowledge Placeholders (Optional)

If `knowledge/` is empty, create placeholders:
- `context/knowledge/patterns/README.md`
- `context/knowledge/anti-patterns/README.md`

These placeholders must:
- define what a pattern/anti-pattern means
- instruct that items must be linked from intents/decisions to be used

---

## Expected Output

At minimum, after execution the repository contains:

```
AGENTS.md

context/
├── .context-mesh-framework.md
├── intent/
│ └── project-intent.md
│ └── feature-.md
├── decisions/
│ └── 001-.md
│ └── 003-.md
│ └── 004-.md
│ └── 005-.md
│ └── 006-.md
│ └── 007-.md
│ └── 008-.md
│ └── 009-*.md
├── knowledge/
│ └── patterns/
│ └── anti-patterns/
├── agents/
│ └── agent-context-bootstrap.md
│ └── agent-brownfield-extractor.md (if available)
│ └── agent-feature-executor.md (if available)
├── evolution/
│ └── changelog.md
```


---

## Definition of Done

- [ ] `context/` folder structure exists and matches Context Mesh conventions
- [ ] `context/.context-mesh-framework.md` exists
- [ ] `context/intent/project-intent.md` exists
- [ ] `context/evolution/changelog.md` exists
- [ ] `AGENTS.md` exists at repository root and references Context Mesh rules
- [ ] Decisions directory uses correct numbering convention
- [ ] Feature inventory is listed and validated for required sections (or gaps are reported)
- [ ] No product feature code was implemented or modified

---

## Verification

Run the following checks:

```bash
# Verify structure
ls -la context
ls -la context/intent context/decisions context/knowledge context/agents context/evolution

# Verify required files exist
test -f AGENTS.md
test -f context/.context-mesh-framework.md
test -f context/intent/project-intent.md
test -f context/evolution/changelog.md
```

# After Completion

**Proceed to:**
- @context/agents/agent-brownfield-extractor.md (for existing projects)
- @context/agents/agent-feature-executor.md (to implement a specific feature)