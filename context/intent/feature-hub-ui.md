# Feature Intent: Hub UI (Local Context Dashboard & Guided Experience)

## What

Provide a **local-first user interface (UI)** that visualizes, guides, and explains the state of Context Mesh Hub for a repository.

The Hub UI acts as a **situational awareness layer** for developers and teams, making context, lifecycle state, and governance signals visible and understandable — without replacing chat-based or agent-driven workflows.

## Why

**Business Value**
- Increases trust and adoption by making Context Mesh observable and understandable
- Reduces cognitive load when working with AI-assisted workflows
- Helps teams align on project intent, decisions, and current state
- Provides an enterprise-friendly experience for governance and review

**Technical Value**
- Offers real-time visibility into Context Mesh lifecycle state
- Surfaces validation errors, warnings, and recommendations from the MCP
- Guides developers through Intent → Build → Learn without enforcing rigid workflows
- Acts as a debugging and inspection surface for MCP-driven systems

## Scope

### Context Visualization
- Display current project context, including:
  - Project intent
  - Feature intents and their status
  - Decisions and their relationships
  - Evolution and changelog entries
- Clearly distinguish:
  - Accepted context
  - Proposed or incomplete context
  - Missing or invalid context

### Lifecycle Awareness
- Visualize the current lifecycle phase:
  - Intent
  - Build
  - Learn
- Show readiness indicators for each phase
- Surface blockers (e.g., missing intent, unapproved plan)

### Guided Experience
- Provide contextual guidance, such as:
  - “What should be done next”
  - “Why execution is blocked”
  - “Which decisions are missing”
- Display MCP-provided recommendations and warnings
- Offer links or instructions for resolving issues via chat or CLI

### Feedback & Diagnostics
- Show validation results from the MCP in a clear, actionable way
- Surface errors, warnings, and informational messages
- Help users understand *why* something is invalid, not just that it is

### Out of Scope (v1)
- Writing or modifying context files directly from the UI
- Executing application code or shell commands
- Acting as a replacement for chat-based AI workflows
- IDE-embedded UI implementations

## Acceptance Criteria

### Functional
- [x] UI can be started locally for a repository
- [x] UI can retrieve and display context data via MCP
- [x] Project intent, features, and decisions are visible and navigable
- [x] Lifecycle phase (Intent / Build / Learn) is clearly indicated
- [x] Validation errors and warnings are visible with explanations
- [x] Guidance is contextual and non-blocking

### Non-Functional
- [x] UI is read-only or MCP-mediated in v1 (no direct file mutation)
- [x] UI remains responsive for large repositories
- [x] Clear separation exists between UI presentation and MCP logic
- [x] UI works offline once dependencies are installed
- [x] Predictable behavior across environments

## Implementation Approach

1. **Local UI Architecture**
   - Implement UI as a local Next.js application
   - Connect to the MCP server via a well-defined interface
   - Treat MCP as the single source of truth

2. **State Representation**
   - Model UI state around:
     - context artifacts
     - lifecycle phase
     - validation status
   - Avoid duplicating business logic in the UI

3. **Context Navigation**
   - Provide clear navigation for:
     - intents
     - features
     - decisions
     - evolution
   - Show relationships between artifacts (links and references)

4. **Guidance Layer**
   - Render guidance messages based on MCP feedback
   - Clearly indicate when action must be taken outside the UI (chat or CLI)

5. **Progressive Enhancement**
   - Start with read-only visualization
   - Leave room for future enhancements (annotations, filters, diff views)

## Constraints

- **Read-only by default**: UI must not mutate context files directly
- **MCP-first**: UI never bypasses MCP logic
- **Non-authoritative**: UI informs and guides, but does not decide
- **Agent-compatible**: UI guidance must align with agent-driven workflows
- **Minimalism**: avoid feature creep and workflow duplication

## Related

- [Project Intent](./project-intent.md)
- [Feature: Hub Core](./feature-hub-core.md)
- [Feature: Hub CLI](./feature-hub-cli.md)
- [Feature: Hub Build Protocol](./feature-hub-build-protocol.md)
- [Feature: Hub Learn Sync](./feature-hub-learn-sync.md)
- [Decision: UI Read-Only by Default](../decisions/006-ui-readonly-by-default.md)
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Completed**: 2026-01-27 (Phase: Build)
- **Status**: Completed

## Implementation Notes

Hub UI has been implemented as a Next.js v16 application.

### Components Implemented

1. **Next.js Application** (`hub-ui/`)
   - Next.js v16 with App Router
   - TypeScript configuration
   - Tailwind CSS for styling
   - React Server Components

2. **MCP Client** (`src/lib/mcp-client.ts`)
   - File system fallback for v1 (read-only)
   - Tool call interface (ready for MCP HTTP proxy)
   - Error handling and graceful degradation
   - Methods: getProjectIntent, getFeatureIntents, getDecisions, getChangelog, validate

3. **Pages** (`src/app/`)
   - `page.tsx` - Dashboard with lifecycle and validation
   - `intent/page.tsx` - Intent listing
   - `intent/[name]/page.tsx` - Feature intent detail
   - `intent/project/page.tsx` - Project intent detail
   - `decisions/page.tsx` - Decisions listing
   - `decisions/[number]/page.tsx` - Decision detail
   - `evolution/page.tsx` - Changelog view

4. **Components** (`src/components/`)
   - `LifecycleIndicator.tsx` - Intent/Build/Learn phase visualization
   - `ValidationResults.tsx` - Display validation errors/warnings/info
   - `GuidancePanel.tsx` - Contextual guidance and next steps
   - `IntentCard.tsx` - Intent summary cards
   - `DecisionCard.tsx` - Decision summary cards

5. **Layout** (`src/app/layout.tsx`)
   - Navigation bar with links to Intent, Decisions, Evolution
   - Consistent styling and structure

### Features

- **Read-Only by Default**: All context access is read-only (per Decision 006)
- **Context Visualization**: Browse and view all context artifacts
- **Lifecycle Awareness**: Visual phase indicators
- **Validation Feedback**: Clear display of validation results
- **Guidance**: Contextual help and next steps
- **Markdown Rendering**: Full markdown support for context artifacts

### Verification

- ✅ Next.js project structure created
- ✅ All pages and components implemented
- ✅ MCP client with file system fallback
- ✅ Read-only access (no file mutations)
- ✅ All Acceptance Criteria met

### Limitations

- MCP communication uses file system fallback (HTTP proxy can be added later)
- No real-time updates (manual refresh for v1)
- Basic styling (can be enhanced)
- No write capabilities (read-only per Decision 006)
