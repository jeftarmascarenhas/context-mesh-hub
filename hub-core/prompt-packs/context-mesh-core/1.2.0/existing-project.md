# Prompt: Add Context Mesh to Existing Project

Use this prompt when you have an existing codebase and want to add Context Mesh (brownfield).

**What happens?** I'll analyze your code and create context that documents:
- What your project does (extracted from code)
- Technical decisions already made
- Existing patterns in your code
- Features that already exist

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Answer** the questions
4. **Review** the analysis
5. **Confirm** to create the files

---

## Prompt

```
I want to add Context Mesh to my existing project.

**FIRST: Analyze my codebase:**

1. Scan the project structure:
   - Check package.json, pyproject.toml, requirements.txt, Cargo.toml, etc. for dependencies
   - Identify languages and frameworks used
   - Find entry points and main modules

2. Identify existing technical decisions:
   - What tech stack is being used?
   - What patterns are evident in the code?
   - What architectural choices have been made?

3. Identify features/modules:
   - What are the main features/components?
   - What does each major module do?

**THEN: Present your findings and ask me:**

Present:
- Languages/frameworks detected
- Tech stack summary
- Main features/modules found
- Architectural patterns observed

Ask:
1. Is this analysis correct? (confirm or correct)
2. What is the project name?
3. What problem does this project solve? (or I can use what I found)
4. Why was this project created?
5. Are there any features or decisions I missed?
6. Which features should I document first? (or should I document all?)

**THEN: Create Context Mesh structure:**

context/
├── .context-mesh-framework.md (framework rules)
├── intent/
│   ├── project-intent.md (from analysis + your input)
│   └── feature-[name].md (one per identified feature)
├── decisions/
│   ├── 001-tech-stack.md (from analysis)
│   └── [002+]-[decision].md (other decisions found)
├── knowledge/
│   ├── patterns/
│   │   └── [pattern].md (patterns found in code)
│   └── anti-patterns/
├── agents/
│   └── (empty)
└── evolution/
    └── changelog.md (current state documented)

Also create AGENTS.md at project root.

**IMPORTANT**:
- Base documentation on actual code analysis
- Ask me to confirm or correct your findings
- Mark all generated context as "Extracted from existing code"
- Include evidence (file paths, code references) in decisions
```

---

## What This Prompt Does

- **Analyzes your codebase** - Scans structure, dependencies, patterns
- **Extracts decisions** - Documents technical choices already made
- **Documents features** - Creates intent files for existing functionality
- **Identifies patterns** - Captures reusable patterns from code
- **Creates full structure** - Sets up complete context/ directory
- **Preserves evidence** - Links context to actual code

---

## After Setup

Once Context Mesh is set up on your existing project:

- **New features**: Use `add-feature.md`
- **Changes**: Use `update-feature.md`
- **Bugs**: Use `fix-bug.md`
- **Learnings**: Use `learn-update.md`

Your existing code is now documented, and future changes will follow the Intent → Build → Learn cycle.

---

## Tips for Brownfield Projects

1. **Start with the most critical features** - Don't try to document everything at once
2. **Let AI analyze first** - It can find patterns you might miss
3. **Correct the analysis** - You know your code best
4. **Update incrementally** - Add more context as you work on different areas
5. **Document decisions as you discover them** - When you find "why was this done this way?", create a decision file
