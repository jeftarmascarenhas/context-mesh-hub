# Context Mesh Core Prompt Pack v1.2.0

## What's New

### New Templates

1. **add-decision.md** - Standalone ADR (create decision without adding a feature)
2. **clarify.md** - Pre-build clarification questions
   - Systematic analysis of feature completeness
   - Targeted questions to reduce ambiguity
   - Completeness scoring and recommendations

3. **checkpoint.md** - Quality gates enforcement
   - Intent → Build gate checks
   - Build → Learn gate checks
   - Blocker identification with actionable fixes

4. **retrospective.md** - Post-implementation reflection
   - Structured reflection (+, -, !, →)
   - Learning capture and context update proposals
   - Action item generation

### Improvements

- All templates now include MCP tool references
- Better integration with Hub CLI slash commands
- Enhanced Plan, Approve, Execute guidance

## Template Index

| Template | Purpose | Phase |
|----------|---------|-------|
| `new-project.md` | Initialize new project | Setup |
| `existing-project.md` | Add to existing codebase | Setup |
| `add-feature.md` | Add new feature | Intent |
| `add-decision.md` | Add standalone ADR | Intent |
| `update-feature.md` | Modify existing feature | Intent |
| `fix-bug.md` | Document bug fix | Intent |
| `create-agent.md` | Create execution agent | Intent |
| `clarify.md` | Pre-build clarification | Intent → Build |
| `checkpoint.md` | Quality gate verification | Intent → Build, Build → Learn |
| `learn-update.md` | Sync learnings | Learn |
| `retrospective.md` | Post-implementation reflection | Learn |

## Workflow Integration

```
Intent Phase           Build Phase            Learn Phase
┌──────────────┐      ┌──────────────┐       ┌──────────────┐
│ add-feature  │      │ Plan         │       │ learn-update │
│ update-feat  │  →   │ Approve      │   →   │ retrospective│
│ fix-bug      │      │ Execute      │       │              │
└──────────────┘      └──────────────┘       └──────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   clarify    │      │  checkpoint  │
│  (optional)  │      │   (gates)    │
└──────────────┘      └──────────────┘
```

## Compatibility

- **Hub Core**: v1.0.0+
- **Hub CLI**: v1.0.0+ (`cm /intent`, `cm /build`, `cm /learn`)
- **Context Mesh Framework**: v1.1.0+

## Migration from 1.0.0

No breaking changes. New templates are additive:
1. Update manifest to use 1.2.0
2. New templates available immediately
3. Existing templates work as before

## Related

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)
- [Context Mesh Hub](https://github.com/jeftarmascarenhas/context-mesh-hub)
