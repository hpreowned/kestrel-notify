# adlc_contract — kestrel-notify

Derived from AGENTS.md by `adlc baseline`; do not edit here, edit AGENTS.md.

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

## Context layer
- context: graphify, serena
- artifact: `graphify-out/graph.json` (check `adlc stale`)
- sensitive paths: none declared
