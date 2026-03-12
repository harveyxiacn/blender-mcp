# Blender MCP Project Review

Date: 2026-03-10

## Scope

Reviewed areas:

- `README.md` and core docs
- `src/blender_mcp/*`
- `addon/blender_mcp_addon/*`
- `tests/*`
- tool/profile inventory from source

## Current Snapshot

- 51 tool modules under `src/blender_mcp/tools`
- 359 total tool registrations in source
- 12 skill groups
- 6 profiles: `minimal`, `skill`, `focused`, `standard`, `extended`, `full`
- default startup surface under `skill`: 32 tools

## Key Findings

### 1. Execution parity gap in automation

Severity: high

- `pipeline` and `quality_audit` are present in `src/blender_mcp/tools_config.py`
- they are exposed through `focused`, `standard`, `full`, and the `automation` skill
- but `addon/blender_mcp_addon/handlers/__init__.py` does not map either category

Impact:

- the tools can be listed by MCP clients
- execution can still fail at addon dispatch time with an unknown category error

Recommendation:

- either add addon handlers immediately
- or remove these modules from stable/default-facing profiles until parity is complete

### 2. Documentation drift was material

Severity: medium

Before this review, core docs still described the project as roughly:

- 200+ tools
- 26 modules
- 11 skills
- `skill` startup size around 31

The current codebase is larger than that, and the roadmap still described some already-implemented areas as future work.

### 3. Environment portability is fragile

Severity: medium

The local `.venv/pyvenv.cfg` embeds an absolute interpreter path. When the repo is copied between machines, `uv run` or `.venv\Scripts\python.exe` can fail before any project code starts.

Recommendation:

- document recovery clearly
- consider excluding portable-hostile virtualenv state from handoff workflows

### 4. Test coverage misses server/addon parity

Severity: medium

Current tests cover config, exports, skill metadata, and some server behavior, but they do not assert that every public server category has a matching addon handler route.

Recommendation:

- add a parity test that compares public execution categories against the addon handler registry
- add one regression test specifically for automation categories

### 5. Legacy root-level test files are easy to miss

Severity: low

`pyproject.toml` points pytest at `tests/`, while several older `test_*.py` files still live at repository root. They are not part of the default pytest path.

Recommendation:

- either migrate them into `tests/`
- or document them as manual/legacy scripts

## Optimization Suggestions

### 1. Generate inventory docs from source

- derive tool counts from decorators
- derive profile counts from `tools_config.py`
- derive skill inventory from `skill_manager.py`
- publish a generated inventory doc in CI to prevent future count drift

### 2. Introduce stable vs experimental capability flags

- keep automation-related modules behind an explicit flag until addon parity exists
- surface that status in docs and tool descriptions

### 3. Add job control for long-running tasks

The addon currently waits on Blender main-thread execution with a timeout-based request model. A job queue would make render, bake, export, and audit flows safer and easier to observe.

Suggested improvements:

- job IDs
- progress updates
- cancellation support
- structured timing / error telemetry

### 4. Tighten the release checklist

- server/addon category parity
- profile counts regenerated
- docs inventory regenerated
- smoke test for `skill`, `focused`, and `full`

## Feature Proposals

### 1. Audit-to-auto-fix workflow

Turn `quality_audit` results into follow-up fix tools:

- fix export naming
- fix missing UVs
- reduce over-budget meshes
- apply release presets per target platform

### 2. Asset recipe manifests

Add declarative recipes for repeatable builds:

- character recipe
- prop recipe
- scene recipe
- export recipe

This would help batch production and make AI-driven pipelines more deterministic.

### 3. Target-aware export validation

Add validators for:

- web
- mobile
- desktop
- hero / AAA

Each validator can check triangle count, materials, texture budgets, naming, and file format policy before export.

### 4. Review bundles

Package a scene review artifact containing:

- viewport screenshots
- audit summary
- export summary
- optional diff vs previous asset version

## Suggested Sequence

1. Fix addon handler parity for `pipeline` and `quality_audit`
2. Add parity tests
3. Auto-generate tool/profile/skill inventory docs
4. Build job control for long-running operations
5. Layer audit-to-auto-fix features on top
