# Contributing to delichen-proofweaver

## Ground Rules

- Preserve the single-writer runtime model.
- Do not make work or verification agents write task state directly.
- Keep orchestration logic explicit in code rather than hiding state transitions in prompts.
- Add tests for any change that affects claim lifecycle, verification semantics, pivot rules, or completion behavior.

## Development Workflow

1. Create or update code under `src/deli_autoresearch/`.
2. Add or update tests under `tests/`.
3. Run:

```bash
python -m pytest -q
```

4. If task asset behavior changes, update `examples/` or `benchmarks/` accordingly.

## Design Boundaries

- `runtime/` is live state, not source material.
- `examples/` are reusable input assets.
- `benchmarks/` are replay scenarios for regression testing.
- `tests/` should validate invariant behavior, not just happy-path output.
