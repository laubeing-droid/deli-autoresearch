# Deli AutoResearch Memory

## 2026-07-01 source-bounded control plane

- Open-web material is never strong evidence by default. It must route as `source_candidate` until an approved source span, formal backend result, or human-reviewed anchor promotes it.
- `Orchestrator` must not write `findings.jsonl` directly after `PROVED`; all verified findings pass through `MemoryRouter` and the disclosure gate first.
- Finding evidence must include a usable `source_id` plus `source_span` or `evidence_path`; otherwise it is written to `failure_registry.jsonl` and treated as `NEEDS_MORE_EVIDENCE`.
- `doctor` writes machine-readable cross-repo state to `runtime/cross_repo_status.json`; runtime output stays ignored by git.
- Legacy Claude-root absolute paths must not remain in tracked text because Playbook scans treat them as stale execution evidence.

## 2026-07-01 pre-release audit hardening

- Public-release scans treat tracked Windows absolute paths as disclosure risk. Source, tests, scripts, docs, examples, and tracked evidence should use placeholders such as `<deli-autoresearch-root>`, `<juris-calculus-root>`, `<legal-math-modeling-root>`, or environment-variable driven paths.
- Cross-repo runtime roots must resolve through `DELI_AUTORESEARCH_ROOT`, `DELI_WORKSPACE_ROOT`, `JURIS_CALCULUS_ROOT`, `MINNAN_PROFILE_ROOT`, or sibling repository discovery. Missing external engines must fail closed instead of validating a claim.
- SPC analysis scripts must take private OCR data from `SPC_OCR_JSON_DIR`; the private data root must not be committed as a default path.
- Deli currently declares no runtime dependencies in `pyproject.toml`; isolated editable install plus `pip check` is the local supply-chain baseline when external vulnerability database queries time out.
