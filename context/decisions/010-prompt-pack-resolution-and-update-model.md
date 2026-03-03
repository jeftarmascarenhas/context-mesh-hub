# Decision 010: Prompt Pack Resolution and Update Model

## Context

Context Mesh Hub is **MCP-first + chat-first** and must provide reliable, repeatable context operations across tools (Cursor, Copilot, Claude, etc.).

The MCP tools that power user actions (e.g., new project, existing project bootstrap, add feature, fix bug, learn sync) require **standardized prompt templates** (Context Mesh “prompt templates”), such as:

- `new-project.md`
- `existing-project.md`
- `add-feature.md`
- `update-feature.md`
- `fix-bug.md`
- `create-agent.md`
- `learn-update.md`

Key requirements:

1. **Deterministic behavior**: the same repo + pinned prompt pack version must produce the same artifacts.
2. **Enterprise-safe customization**: allow repo-level overrides without forking Hub.
3. **Offline-first**: Hub must work without network by default (bundled fallback).
4. **Decoupled updates**: prompt templates must be updatable without requiring CLI/MCP upgrades (when MCP protocol is unchanged).
5. **Governance**: prompts and generated artifacts must be auditable (source + version + hash).

The Hub currently risks being non-functional if MCP tools do not resolve and use these prompts consistently.

## Decision

We adopt **Option 2 (Decoupled Prompt Packs, no package registry dependency)**:

### 1) Prompt Packs are versioned directories of `.md` templates

A Prompt Pack is a filesystem directory containing Context Mesh prompt templates.

Canonical layout (local cache):

`~/.context-mesh-hub/prompt-packs/<packName>/<version>/*.md`

Example:

`~/.context-mesh-hub/prompt-packs/context-mesh-core/1.1.0/add-feature.md`

### 2) Prompt Resolution Order (deterministic)

When a MCP tool needs a template, it MUST resolve using this strict order:

1. **Repo override** (highest priority)
   - `<repoRoot>/.context-mesh/prompts/<template>.md`

2. **Pinned cached pack** (if present locally)
   - `~/.context-mesh-hub/prompt-packs/<packName>/<version>/<template>.md`

3. **Bundled fallback pack** (shipped with Hub)
   - `internal://prompt-packs/<packName>/<bundledVersion>/<template>.md`

This guarantees enterprise override + pin reproducibility + offline safety.

### 3) Pin mechanism (repo-first)

Each repo pins the active Prompt Pack via a manifest file stored in-repo:

`context/hub-manifest.json`

Minimum schema:

```json
{
  "promptPack": {
    "name": "context-mesh-core",
    "version": "1.10.0",
    "source": "cached|bundled"
  }
}
```

- source=cached means “must use local cache if available”.
- source=bundled means “use embedded pack only”.

> Repo override still wins regardless of pin.

### 4) MCP tool surface is “prompt-driven” (mandatory)

Hub MCP MUST expose semantic tools that map to prompt templates (not paths):

- hub.intent.newProject → uses new-project.md
- hub.intent.existingProject → uses existing-project.md
- hub.intent.addFeature → uses add-feature.md
- hub.intent.updateFeature → uses update-feature.md
- hub.intent.fixBug → uses fix-bug.md
- hub.intent.createAgent → uses create-agent.md
- hub.learn.sync → uses learn-update.md

Tools MUST:

- resolve template via the resolution order above
- record provenance (pack name/version/source + template hash)
- generate/update only Context Mesh artifacts (no direct product code generation)

### 5) Updates: download + cache, without packages

Prompt Pack updates are performed by Hub/CLI via network download (no npm/pip packages required).

Hub MUST support:

- hub.prompts.status
    - shows current pinned pack, available cached versions, bundled version

- hub.prompts.install(packName, version, sourceURL?)
    - downloads an archive and installs into local cache

- hub.prompts.use(packName, version)
    - updates context/hub-manifest.json to pin that version

- hub.prompts.verify(packName, version)
    - verifies integrity (hash manifest / signature if available)

Default distribution channel for packs:
- GitHub Releases (zip/tar.gz) OR official static URL
- Enterprise can mirror internally

### 6) Integrity and auditing

Every time a template is used, Hub MUST write a provenance block into the generated/updated artifact(s), or into an internal run log:

- packName

- packVersion

- templateName

- templateHash

- resolutionSource (repoOverride | cached | bundled)

This is required for auditability and debugging.

## Rationale

- **Decoupled updates:** enables rapid iteration on templates without forcing CLI upgrades.

- **Enterprise compatibility:** repo overrides allow company-specific policy/custom templates.

- **Reproducibility:** pinning ensures stable behavior across machines and time.

- **Offline-first:** bundled fallback prevents “first run” dependency on network.

- **Correctness:** mandates that MCP tools are prompt-driven, avoiding a “tools exist but do nothing useful” failure mode.

## Alternatives Considered

1. Bundled-only prompts (coupled updates)
    - Pros: simplest
    - Cons: every prompt update requires CLI upgrade (not acceptable for enterprise velocity)

2. Prompt packs as npm/pip packages
    - Pros: easy versioning
    - Cons: enterprise registry restrictions, auth, supply-chain policy, higher friction

3. Database-based registry
    - Pros: centralized
    - Cons: violates repo-first v1 constraint and adds operational complexity

## Implementation Details
### Template naming

Templates MUST use these canonical names:
- new-project.md
- existing-project.md
- add-feature.md
- update-feature.md
- fix-bug.md
- create-agent.md
- learn-update.md

### Bundled fallback location (Hub repo)

Hub source tree should include:

`packages/hub/src/prompt-packs/context-mesh-core/<bundledVersion>/*.md`

## Bundled packs are included in published artifacts.

### Download format (recommended)

Each release provides:

- context-mesh-core-1.10.0.zip
    - contains <packName>/<version>/*.md
    - optional manifest.json with hashes

### Error behavior

- If pinned pack version is missing in cache and source is cached,
Hub MUST fall back to bundled and emit a warning:
    - “Pinned pack not found in cache; using bundled fallback”

- If required template is missing in all sources,
Hub MUST fail the tool call with a clear error:
    - “Template not found: add-feature.md”

## Consequences

- Hub must ship with at least one bundled pack version.
- Hub must implement cache install/use/verify workflow.
- MCP tools must be explicitly mapped to templates.
- Feature intents and build protocol must reference this decision.

## Related
`@context/intent/feature-hub-core.md`

`@context/intent/feature-hub-build-protocol.md`

`@context/intent/feature-hub-cli.md`

`@context/intent/feature-hub-learn-sync.md`

`@context/decisions/003-mcp-tooling-and-authority.md (if exists; link the authority model)`

`@context/decisions/009-context-evolution-rules.md`

## Outcomes

**Initial Implementation (2026-01-27):**

- ✅ Prompt resolver module implemented with resolution order (repo override > cached > bundled)
- ✅ Prompt pack manager implemented (install, use, verify operations)
- ✅ Bundled fallback templates created (7 canonical templates)
- ✅ MCP tools added for prompt pack management (status, install, use, verify)
- ✅ Intent/build/learn tools converted to be prompt-driven
- ✅ Manifest reading/writing implemented for `context/hub-manifest.json`
- ✅ Provenance tracking implemented (pack/version/template/hash/source)
- ✅ Feature intents updated to reference Decision 010
- ✅ Missing acceptance criteria added to feature-hub-core.md

**What Worked:**
- Resolution order provides clear priority (repo override wins)
- Bundled fallback ensures offline-first behavior
- Manifest-based pinning enables reproducibility
- Provenance tracking supports auditability

**Limitations:**
- Template rendering is basic (returns template content + inputs, actual rendering happens in agent layer)
- Pack installation requires network access (offline install not yet supported)
- Cache directory structure is fixed (no custom cache locations yet)

## Status

**Created:** 2026-01-27 (Phase: Intent)

**Status:** Accepted
