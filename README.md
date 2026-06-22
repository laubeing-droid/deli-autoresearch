# Deli_AutoResearch

Local Python implementation of the Deli_AutoResearch protocol.

## What Runs Today

- Filesystem-backed runtime under `runtime/`
- Task registry, state files, logs, and claim tracking
- Orchestrator and heartbeat single-pass commands
- Built-in templates: `general_research` and `math_proof`
- Completion policy with explicit tail-pass execution
- Task asset loading from adjacent `seed_directions.json`
- Replay benchmarks for regression scenarios
- Two backends:
  - `mock` for tests and dry runs
  - `codex-bridge` for real multi-session use

## Install

```bash
pip install -e .
```

Or run without install:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . doctor
```

## Start A Math Proof Task

Create a task spec file, for example `task_spec.md`:

```md
# goal
Prove or refute the target statement.

# milestones
- Produce candidate lemmas
- Validate or reject candidate claims

# success_criteria
- At least one validated finding advances the proof or refutation

# constraints
- Strict JSON-only agent responses

# conjecture
Your theorem statement here

# known_lemmas
- Add any known lemmas here
```

Initialize the task:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . init-task --task-id proof-001 --template math_proof --task-spec-file task_spec.md
```

If `task_spec.md` sits beside a `seed_directions.json`, the framework will load those seed directions automatically instead of the template defaults.

## Task Asset Library

The repo now includes reusable proof-task assets under `examples/`, for example:

- `examples/math_proof/induction/sum_of_odds/`
- `examples/math_proof/combinatorics/triangular_numbers/`
- `examples/math_proof/inequalities/am_gm_n2/`

These are intended as reusable inputs for real runs and regression tasks.

## Real Multi-Session Flow

Use the `codex-bridge` backend when you want other Codex sessions to do the work/verification.

Run one orchestrator pass:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . --backend codex-bridge run-orchestrator-once
```

That command writes request files into:

- `runtime/bridge/requests/`

Each request file contains:

- `instruction`: the exact prompt to give another Codex session
- `prompt`: the structured JSON context
- `agent_id`: the response filename to write back

The responding session must write strict JSON results to:

- `runtime/bridge/responses/<agent_id>.json`

Example response for a work request:

```json
{
  "summary": "Proposed two candidate lemmas.",
  "claims": [
    {
      "claim_text": "Lemma A implies B under condition C",
      "evidence": [
        {
          "source_kind": "web",
          "url": "https://example.com",
          "quote": "supporting source"
        }
      ],
      "source_kind": "web",
      "verifiable": true,
      "support_kind": "new"
    }
  ]
}
```

Example response for a verification request:

```json
{
  "claim_id": "claim_123456789abc",
  "verdict": "needs_more_evidence",
  "evidence_strength": "weak",
  "summary": "The direction is plausible but the evidence is not yet sufficient.",
  "supporting_evidence": []
}
```

Inspect bridge state:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . --backend codex-bridge bridge-status --show-files
```

Heartbeat pass:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . run-heartbeat-once
```

## Replay Benchmark

Run a canned scenario to regression-test orchestration, validation, and tail-pass behavior:

```bash
PYTHONPATH=src
python -m deli_autoresearch.cli --workspace . run-benchmark --scenario benchmarks/sum_of_odds_tail_pass.json
```
