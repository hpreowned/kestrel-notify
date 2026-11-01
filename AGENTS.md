# AGENTS.md — kestrel-notify

<!-- Written by the team. Keep it short; agents read this on every task. Do NOT
     duplicate what pom.xml / csproj / pyproject / package.json / CODEOWNERS encode.
     Backticked paths must exist in THIS repo (lint checks). For paths in another repo
     write `repo:path`, e.g. `kestrel-ops:adr/0007-rate-limit-per-carrier.md`. -->

## Build, test, run, lint
- Install: `uv venv -p 3.12 .venv && uv pip install -p .venv/bin/python -e ".[dev]"`. Test: `.venv/bin/pytest -q`.
- Run: `.venv/bin/uvicorn notify.main:app --reload`. Health: `GET /healthz`.

## Conventions
- Wire JSON is snake_case (`notify/models.py`). Channels implement the interface in
  `notify/channels/base.py`; real senders are stubs writing to an in-memory outbox.
- Secrets come from the environment only (`notify/settings.py`); never commit one.

## Do not touch
- `notify/legacy_fanout.py` — scheduled for removal; do not extend.

## Where things are explained
- `README.md` here; incident and ticket history lives in the kestrel-ops repo (`kestrel-ops:tickets/`).

<!-- adlc:routing:start -->
## Context routing (kit-owned — do not edit; `adlc init` rewrites this section)

Pick the tool by the shape of the question, not by habit:
- **Graph** (`/graphify query|path|explain`, or `adlc query --level project|org` for
  cross-repo questions): structural questions — who calls this, what breaks if this
  changes, path between two things, which subsystem/community owns it, *why* something
  exists (docs and ADRs are nodes too).
- **grep / file read**: literals — an error string, a config key, a feature flag, a
  column name, a log line. The graph will not beat grep here; do not try.
- **Serena (LSP)**: symbol-precise edits and references — rename, replace a symbol body,
  insert after a symbol, find references across files with type awareness.
- Before trusting the graph run `adlc stale`; exit 0 fresh, 1 usable, 2 rebuild first.
  On a feature branch run `adlc baseline --incremental` before structural queries.
- Levels: this repo's graph answers inside-repo questions; `--level project` answers
  "which consumer breaks"; `--level org` answers "which team/project is affected".
<!-- adlc:routing:end -->

```yaml
adlc:
  schema: 1
  context: [graphify, serena]
  artifact: graphify-out/graph.json
  sensitive: []
  freshness: two-tier
  kit: 0.1.5
```
