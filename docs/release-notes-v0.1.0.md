# Deli AutoResearch v0.1.0

Initial local release of `Deli AutoResearch`.

## Scope

This release introduced the filesystem-backed research orchestration runtime:

- explicit task registry and per-task state;
- claim, evidence, finding, and direction lifecycle records;
- independent work and verification phases;
- stall-pressure and structural pivot logic;
- tail-pass completion policy;
- reusable task assets under `examples/`;
- replay benchmark support;
- `codex-bridge` request/response backend for multi-session execution.

## Boundary

The release did not claim:

- formal proof of arbitrary legal or mathematical outcomes;
- verified facts from model output alone;
- public inclusion of private legal workflows, private benchmark sets, or commercial rule assets.

## Validation

The historical v0.1.0 validation command was:

```powershell
python -m pytest -q
```

For the current validation baseline, read `PLANS.md` and the latest report under `docs/audit/`.
