# Execution State

This file is a human-readable planning snapshot. The authoritative state remains on disk under `specs/`, `state/`, `runtime/`, and git history.

## Current Snapshot

```text
status: MAINTENANCE_AND_RELEASE_HARDENING
last_verified_commit: b6d56b25ab2fa293529f20df0dff8037bbe0f4b3
branch_state: main...origin/main [ahead 4]
local_test_baseline: 158 passed
pre_release_status: BLOCKED_EXTERNAL_VULNERABILITY_DB
```

The local code/test/disclosure gates are green. External vulnerability database lookup is not green because `pip-audit` timed out against the remote advisory service through the configured local proxy.

## Completed Tracks

### Track A: Source-Bounded Control Plane

- Source registry and retrieval policy are implemented.
- Open-web and model-generated material remain candidate-only by default.
- Memory routing sends weak or incomplete evidence to failure/candidate streams.
- Disclosure gate prevents weak evidence from being published as a finding.

### Track B: Cross-Repo Verification Bridges

- Deli can call juris-calculus runtime checks through a local backend adapter.
- Lean theorem manifest discovery routes through `LEGAL_MATH_MODELING_ROOT` or workspace probes.
- Missing external engines fail closed.
- `doctor` emits machine-readable cross-repo status under ignored runtime output.

### Track C: Litigation And Research Automation

- `legal_proof` template supports Horn/AAF grounded-extension verification flows.
- Batch litigation helpers connect Deli cases to juris-calculus certificates and traces.
- Research automation ranks breakthrough candidates, builds capability maps, and replays benchmarks.

### Track D: Pre-Release Hygiene

- Tracked machine-specific paths were removed from source, tests, scripts, docs, examples, and historical evidence.
- Private SPC OCR input now requires `SPC_OCR_JSON_DIR`.
- Public docs use placeholders and environment variables instead of local machine paths.

## Verification Gates

| Gate | Current status | Evidence |
| --- | --- | --- |
| Full Deli pytest | PASS | `python -m pytest -q` -> `158 passed` |
| Source-bounded subset | PASS | source registry, retrieval policy, memory router, trial harness, search frontier, verification backend, disclosure gate, local-history profile |
| Path resolver regression | PASS | Banach, cross-repo bridge, legal proof bridge tests |
| Compile check | PASS | `python -m compileall -q src scripts spc_analysis` |
| Disclosure scans | PASS | no tracked matches for Windows absolute paths, legacy Claude root, Codex root, private sync root, local proxy literal |
| Isolated editable install | PASS | temporary venv install and `pip check` |
| External vulnerability DB | BLOCKED | `pip-audit` timed out against remote advisory service |

## Next Work

1. Re-run external vulnerability audit when the advisory service is reachable through the configured proxy.
2. Keep public docs aligned with the source-bounded and fail-closed model.
3. Expand examples only when the verifier path is deterministic and covered by tests.
4. Keep commercial data, private rule libraries, lawyer workflows, litigation strategy, and private benchmarks outside the public auditable kernel.

## Non-Goals

- No push, tag, release, or GitHub visibility change from this local state file.
- No claim that LLM output is a verified fact.
- No claim that empirical runs are formal proofs.
- No weakening of checker acceptance standards or attack/exception/priority semantics.
