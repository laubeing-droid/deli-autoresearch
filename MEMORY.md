# Deli AutoResearch Memory

## 2026-07-01 source-bounded control plane

- Open-web material is never strong evidence by default. It must route as `source_candidate` until an approved source span, formal backend result, or human-reviewed anchor promotes it.
- `Orchestrator` must not write `findings.jsonl` directly after `PROVED`; all verified findings pass through `MemoryRouter` and the disclosure gate first.
- Finding evidence must include a usable `source_id` plus `source_span` or `evidence_path`; otherwise it is written to `failure_registry.jsonl` and treated as `NEEDS_MORE_EVIDENCE`.
- `doctor` writes machine-readable cross-repo state to `runtime/cross_repo_status.json`; runtime output stays ignored by git.
- Legacy Claude-root absolute paths must not remain in tracked text because Playbook scans treat them as stale execution evidence.
