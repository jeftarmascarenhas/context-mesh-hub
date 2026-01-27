# Hub UI - Context Mesh Hub Local Dashboard

Local-first Next.js UI for visualizing and navigating Context Mesh context.

## Installation

```bash
cd hub-ui
pnpm install
```

## Development

```bash
pnpm dev
```

Starts the development server at http://localhost:3000

## Build

```bash
pnpm build
pnpm start
```

## Features

- **Context Visualization**: Browse intents, decisions, and evolution
- **Lifecycle Awareness**: Visualize Intent → Build → Learn phases
- **Validation Feedback**: Display validation errors and warnings
- **Guidance**: Contextual guidance and next steps

## Architecture

- Next.js v16 with App Router
- React Server Components
- Tailwind CSS for styling
- MCP client for context access (file system fallback for v1)

## Read-Only by Default

Per Decision 006, the UI is read-only by default. All context access is through MCP tools or safe file system reading.
