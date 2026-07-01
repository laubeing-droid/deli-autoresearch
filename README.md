# Deli AutoResearch

[![CI](https://github.com/laubeing-droid/deli-autoresearch/actions/workflows/ci.yml/badge.svg)](https://github.com/laubeing-droid/deli-autoresearch/actions/workflows/ci.yml)

`Deli AutoResearch` is a filesystem-backed orchestration framework for long-horizon proof and source-bounded research. It coordinates work agents, verification backends, explicit evidence routing, stall/pivot control, and tail-pass completion.

It is not a one-shot prover and it is not an open-web autonomous researcher. Deli lets candidates be proposed, but findings are admitted only through source and verification gates.

## Current Baseline

- Python: `>=3.12`
- Runtime dependencies: none declared in `pyproject.toml`
- Current full local test command: `python -m pytest -q`
- Current pre-release audit report: `docs/audit/pre-release-audit-2026-07-01.md`
- Live runtime state: ignored under `runtime/`

## Core Guarantees

- Single writer: only the controller updates task state and runtime streams.
- Strict separation: work candidates and verification verdicts are different objects.
- Three verdicts only: `validated`, `rejected`, `needs_more_evidence`.
- Fail closed: truncation, unknown backend status, missing source span, or weak evidence cannot become a finding.
- Candidate-only LLM/web output: `derived`, `model_generated`, and open-web material cannot stand alone as verified findings.
- Source-bounded routing: approved source spans, formal backend output, or human-reviewed anchors are required before publication.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/deli_autoresearch/` | Runtime, CLI, orchestrator, templates, source policy, memory routing, verification adapters |
| `tests/` | Unit and integration coverage for lifecycle, gates, backends, and cross-repo adapters |
| `config/source_registry.example.yml` | Example registry for source-bounded retrieval |
| `schemas/` | Machine-readable contracts for source registry and spec run results |
| `examples/` | Reusable task specs and seed directions |
| `benchmarks/` | Replay scenarios |
| `docs/` | Public operational, research, publishing, and audit documentation |
| `specs/` | Spec-driven implementation history and evidence |
| `state/` | Tracked human decisions and cross-repo coordination locks |
| `runtime/` | Ignored live runtime state |

## Install

```powershell
python -m pip install -e .
```

Run the CLI through the installed entrypoint:

```powershell
deli-autoresearch --workspace . doctor
```

Or run directly from source:

```powershell
$env:PYTHONPATH = "src"
python -m deli_autoresearch.cli --workspace . doctor
```

## Quick Start

Initialize a math proof task:

```powershell
deli-autoresearch --workspace . init-task --task-id proof-001 --template math_proof --task-spec-file examples/math_proof/induction/sum_of_odds/task_spec.md
```

Run one mock orchestrator pass:

```powershell
deli-autoresearch --workspace . --backend mock run-orchestrator-once
```

Run one filesystem bridge pass:

```powershell
deli-autoresearch --workspace . --backend codex-bridge run-orchestrator-once
```

Inspect pending bridge requests and returned responses:

```powershell
deli-autoresearch --workspace . --backend codex-bridge bridge-status --show-files
```

Run a replay benchmark:

```powershell
deli-autoresearch --workspace . run-benchmark --scenario benchmarks/sum_of_odds_tail_pass.json
```

## Runtime Model

The runtime is intentionally file-backed.

| Runtime path | Meaning |
| --- | --- |
| `runtime/registry.json` | Scheduler-facing task registry |
| `runtime/tasks/<task_id>/state/` | Progress, claims, directions, and task spec |
| `runtime/tasks/<task_id>/logs/` | Work, verification, findings, failures, heartbeat, and iteration logs |
| `runtime/bridge/requests/` | Strict JSON requests for external work or verification sessions |
| `runtime/bridge/responses/` | Strict JSON responses keyed by request or agent id |
| `runtime/cross_repo_status.json` | Machine-readable status written by `doctor` |

Runtime data is local state and must not be committed.

## Source-Bounded Research

Deli can process model output and web discoveries, but those objects are candidates. A publishable finding must pass through the source registry, retrieval policy, trial harness, memory router, disclosure gate, and an accepted evidence class.

Read:

- `docs/source_bounded_research.md`
- `docs/research/methodology.md`
- `docs/research/formal-trust-boundary.md`

## Cross-Repo Adapters

Deli can call adjacent formal/runtime repositories through environment variables or sibling-repo discovery:

| Variable | Purpose |
| --- | --- |
| `DELI_AUTORESEARCH_ROOT` | Explicit Deli workspace root |
| `DELI_WORKSPACE_ROOT` | Alternate Deli workspace root for scripts |
| `JURIS_CALCULUS_ROOT` | juris-calculus runtime/kernel checkout |
| `LEGAL_MATH_MODELING_ROOT` | Lean theorem manifest and formal-spec companion repo |
| `MINNAN_PROFILE_ROOT` | Local-history source-bounded profile root |
| `SPC_OCR_JSON_DIR` | Private SPC OCR input directory for analysis scripts |

If a required external engine cannot be found, Deli must report backend unavailability rather than validate the claim.

## Verification

Run the local suite:

```powershell
python -m pytest -q
```

Compile source and helper scripts:

```powershell
python -m compileall -q src scripts spc_analysis
```

Run source-bounded gates directly:

```powershell
python -m pytest tests/test_source_registry.py tests/test_retrieval_policy.py tests/test_memory_router.py tests/test_trial_harness.py tests/test_search_frontier.py tests/test_verification_backends.py tests/test_disclosure_gate.py tests/test_local_history_profile.py -q
```

Run pre-release disclosure scans before publishing:

```powershell
git grep -n -E '[A-Z]:\\' -- .
git grep -n -F '<legacy-local-root-token>' -- .
git grep -n -F '<local-proxy-endpoint>' -- .
```

Replace the placeholder tokens with the local strings being audited. These scans should return no matches in tracked files. Do not treat external vulnerability scans as passed unless the vulnerability database query completes.

## Documentation

- `docs/README.md`: documentation index
- `docs/publishing.md`: local pre-publication checklist
- `docs/claude-code-operations.md`: spec-driven operations guide
- `docs/research/template-authoring-guide.md`: template contract
- `CHANGELOG.md`: project changes
- `PLANS.md`: current local execution state

## Naming

`Deli AutoResearch` names the orchestration layer. It is the process controller that keeps research bounded, stateful, and auditable.
