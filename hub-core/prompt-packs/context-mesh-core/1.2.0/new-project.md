# Prompt: Initialize Context Mesh for New Project

Use this prompt when starting a brand new project from scratch.

**What gets created?** A `context/` folder structure that captures:
- **Intent** - What you're building and why (project-intent.md, optionally feature intents)
- **Decisions** - Technical choices (ADRs) - tech stack (if provided), optionally feature decisions
- **Knowledge** - Patterns and anti-patterns (structure ready)
- **Evolution** - Changelog and learnings (structure ready)

**Flexibility**: You can create features now or add them later using `add-feature.md`

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Answer** the questions
4. **Review** generated files
5. **Build** - Use the execution prompt to start coding

---

## Prompt

```
I'm starting a new project with Context Mesh.

Ask me:
1. Project name?
2. Project type? (web app, API, mobile, CLI, library, etc.)
3. What problem does it solve?
4. Why is this important? (business value)
5. Project acceptance criteria? (overall project criteria)
6. Tech stack? (if known)
   - If tech stack provided, also ask:
     - Why this tech stack? (Rationale)
     - What alternatives did you consider?
7. Do you want to add features now? (y/n)
   - If YES: For each feature, ask:
     - Feature name?
     - What does this feature do and why do we need it?
     - Acceptance criteria for this feature?
     - Technical approach for this feature? (What technical solution will be used?)
     - Why this approach? (Rationale)
     - What alternatives did you consider?
   - If NO: Skip feature creation (user can use add-feature.md later)
8. Do you have any initial patterns or conventions? (y/n) (optional)
   - If YES: For each pattern, ask:
     - Pattern name?
     - What is this pattern? (description)
     - When to use this pattern?
     - Example or code structure?
   - If NO: Skip pattern creation (patterns can be added later via learn-update.md)

Then create this structure:

context/
├── .context-mesh-framework.md (ALWAYS create - framework rules and patterns)
├── intent/
│   ├── project-intent.md
│   └── feature-[name].md (only if user answered YES to question 7, one per feature with complete information)
├── decisions/
│   ├── 001-tech-stack.md (if tech stack provided)
│   └── [002+]-[feature-name].md (only if features were created, one per feature, starting from 002 if tech-stack exists, or 001 if not)
├── knowledge/
│   ├── patterns/
│   │   └── [pattern-name].md (only if user answered YES to question 8)
│   └── anti-patterns/
├── agents/
│   └── (empty for now)
└── evolution/
    └── changelog.md

Also create AGENTS.md at project root.

**Note**: 
- If user answered NO to question 7, inform them: "Project structure created. Use add-feature.md to add features when ready."
- If user answered NO to question 8, inform them: "Patterns can be added later via learn-update.md when you discover reusable patterns during implementation."

---
TEMPLATES:
---

PROJECT-INTENT.MD:
---
# Project Intent: [PROJECT_NAME]

## What
[Project description]

## Why
[Business value, problem it solves]

## Acceptance Criteria
- [Criterion 1]
- [Criterion 2]

## Scope
- [Feature 1]
- [Feature 2]

## Status
- **Created**: [TODAY'S DATE] (Phase: Intent)
- **Status**: Draft
---

FEATURE-[NAME].MD:
---
# Feature: [FEATURE_NAME]

## What
[What this feature does]

## Why
[Why we need it]

## Acceptance Criteria
- [Criterion 1]
- [Criterion 2]

## Related
- [Project Intent](project-intent.md)
- [Decision: [Feature Name]](../decisions/[number]-[feature-name].md)

## Status
- **Created**: [TODAY'S DATE] (Phase: Intent)
- **Status**: Draft
---

Create all files based on my answers.

**Important**: 
- Always create project-intent.md, structure folders, and AGENTS.md
- Only create feature files and feature decisions if user answered YES to question 7
- Only create pattern files if user answered YES to question 8
- If user answered NO to question 7, inform them they can use add-feature.md to add features later
- If user answered NO to question 8, inform them patterns can be added later via learn-update.md

**Bidirectional Links**: Create proper links between features and decisions:
- Feature files must link to their decision files using format: `- [Decision: Name](../decisions/[number]-[name].md)`
- Decision files must link back to their feature files using format: `- [Feature: Name](../intent/feature-[name].md)`
```

---

## Execute: Build the Project

After Context Mesh is created:

```
Load @context files and build the project.
```

---

## What This Prompt Does

- **Creates `context/` folder** with complete structure
- **Creates `project-intent.md`** - Main project intent
- **Creates `001-tech-stack.md`** - If tech stack was provided (with rationale and alternatives)
- **Creates `changelog.md`** - Initial changelog
- **Creates `AGENTS.md`** - AI agent router at project root
- **Optionally creates features** - If you answer YES to "add features now":
  - **Creates `feature-*.md`** - One per feature (complete with What, Why, Acceptance Criteria)
  - **Creates `[next-number]-[feature-name].md`** - One decision per feature (technical approach with rationale and alternatives)
- **Optionally creates patterns** - If you answer YES to "initial patterns":
  - **Creates `patterns/[pattern-name].md`** - Reusable patterns and conventions

**Flexibility**: 
- **Start simple**: Answer NO to features/patterns questions, then use `add-feature.md` or `learn-update.md` when ready
- **Start complete**: Answer YES to features/patterns questions, get everything set up at once

---

## Next Steps

- **Add feature**: Use `add-feature.md` (if you didn't create features during initialization)
- **Fix bug**: Use `fix-bug.md`
- **Update feature**: Use `update-feature.md`
- **Start building**: Load @context files and begin implementation
