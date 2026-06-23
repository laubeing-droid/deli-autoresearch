# AGENTS.md -- Deli AutoResearch project rules

> Loaded automatically at session start. Every AI agent MUST follow.

## Repository Identity

- Owner: laubeing-droid
- Remote: https://github.com/laubeing-droid/deli-autoresearch
- Python: 3.12.5
- Purpose: Autonomous long-cycle research framework with work/verification agent loop

## Architecture Rules (NON-NEGOTIABLE)

1. Single writer: only the controller process may modify task state files and data stream files.
2. Work/verification agents return STRICT JSON only. Never write to state files directly.
3. Fresh session per round: new agent for each work cycle, new agent for each verification.
4. Verification per-claim, parallel fan-out, independent agents.
5. Verdict: `validated` | `rejected` | `needs_more_evidence` -- three states only.
6. `derived` / `model_generated` sources CANNOT constitute a valid finding without strong source backing.
7. Orchestrator does process arbitration only -- never subjective content judgment.
8. Fail-closed: any non-converged or truncated result is treated as failure.

## Stall & Pivot State Machine

- `validated`: add findings, clear stall pressure, clear consecutive evidence counter.
- `needs_more_evidence`: stall +0.5, consecutive evidence +1.
- `rejected`: stall +1, consecutive evidence reset to 0.
- Consecutive `needs_more_evidence` >= 2: force exit current claim.
- Stall pressure >= 2: force STRUCTURAL pivot (strategy type MUST change).
- Stall pressure >= 4: mark `needs_human_attention`, set status `paused_for_human`.

## Build & Test

```powershell
cd D:\Claude\数学证明自动研究
pytest tests/ -q -ra
```

## Cross-Repo

- juris-calculus bridge consumes v3.0 `grounded_extension` fields (`derived_bound`, `converged`, `truncated`).
- legal-math-modeling Lean theorems provide the formal specification.
- Any bridge protocol change requires cross-repo integration test pass.

## Communication

- Chinese with user; English in code, comments, commit messages.
- Never fabricate calibration data.
- `.olean` and build artifacts are NEVER committed.
