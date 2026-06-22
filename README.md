# delichen-proofweaver

`delichen-proofweaver` is a long-horizon proof research framework for running multi-round mathematical proof exploration with explicit state, verification, pivot rules, and tail-pass completion.

It is not a one-shot prover. It is a proof-process orchestrator.

## What It Does

- Tracks proof work as explicit runtime state under `runtime/`
- Treats claims, evidence, findings, and directions as first-class objects
- Separates `work` from `verification`
- Enforces pivot rules when progress stalls
- Supports completion policies with an explicit tail pass
- Loads reusable task assets and seed directions from `examples/`
- Supports replay benchmarks for regression testing
- Supports a real multi-session bridge backend through filesystem request/response envelopes

## Project Shape

- `src/deli_autoresearch/`
  Core runtime, CLI, orchestrator, heartbeat service, templates, and bridge backend
- `examples/`
  Reusable proof-task assets
- `benchmarks/`
  Replay scenarios for regression testing
- `tests/`
  Unit and integration coverage for orchestration behavior

## Install

```bash
pip install -e .
```

Or run directly from source:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . doctor
```

## Quick Start

Initialize a proof task:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . init-task --task-id proof-001 --template math_proof --task-spec-file examples/math_proof/induction/sum_of_odds/task_spec.md
```

Run one local orchestrator pass with the bridge backend:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . --backend codex-bridge run-orchestrator-once
```

Inspect pending bridge work:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . --backend codex-bridge bridge-status --show-files
```

## Runtime Model

The runtime is filesystem-backed.

- `runtime/registry.json`
  Global task registry and scheduler-facing metadata
- `runtime/tasks/<task_id>/state/`
  Per-task progress, claims, directions, and task spec
- `runtime/tasks/<task_id>/logs/`
  Work, verification, heartbeat, findings, and iteration logs
- `runtime/bridge/requests/`
  Requests for external work/verification sessions
- `runtime/bridge/responses/`
  Returned JSON results for those requests

Runtime directories are intentionally ignored by git.

## Proof Task Assets

The repository includes reusable math-proof assets:

- `examples/math_proof/induction/sum_of_odds/`
- `examples/math_proof/combinatorics/triangular_numbers/`
- `examples/math_proof/inequalities/am_gm_n2/`

If a task spec sits beside `seed_directions.json`, those directions are loaded automatically during initialization.

## Multi-Session Bridge

`codex-bridge` is the real execution path for multi-session work.

One session runs the orchestrator. Other sessions consume files written under:

- `runtime/bridge/requests/*.json`

Each request contains:

- `instruction`
- `prompt`
- `agent_id`
- `kind`

Responders must write strict JSON to:

- `runtime/bridge/responses/<agent_id>.json`

## Replay Benchmarks

Run the built-in tail-pass regression scenario:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . run-benchmark --scenario benchmarks/sum_of_odds_tail_pass.json
```

## Development

Run tests:

```bash
python -m pytest -q
```

Print CLI help:

```bash
PYTHONPATH=src
python -c "import sys; sys.path.insert(0, 'src'); from deli_autoresearch.cli import build_parser; build_parser().print_help()"
```

## Status

Current implementation includes:

- Explicit claim lifecycle tracking
- Strong/weak evidence handling
- Independent verification flow
- Stall pressure and forced pivot logic
- Tail-pass completion
- Task asset loading
- Replay benchmark support

## Naming

`ProofWeaver` means the system weaves isolated claims, lemmas, and evidence into a structured proof process over multiple rounds instead of pretending to solve the whole proof in one shot.
