# P4-G08~G09 Status — JC Production Attack Compiler

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 7.3, P4-G08 and P4-G09
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P4-G08: Repair JC Production Attack Compiler

**PASS. No repair needed.**

Production attack path: `FixpointEvaluator.evaluate_horn()` → Horn closure → `compileAttacks()` (canonical_adapter.py) → DungAAF.

Key evidence:
- `compiler_core/evaluator.py`: `evaluate_horn()` produces monotone Horn closure
- `compiler_core/canonical_adapter.py`: `adapt_jc_rule()` maps production rules to canonical format
- `tests/spec/test_attack_compiler.py`: 8/8 tests pass (attack compilation, soundness, completeness)

Production path closes through canonical adapter — not a parallel implementation.

## P4-G09: Remove Synthetic Shadow Semantics

**PASS. Shadow harness is a control, not the sole truth source.**

The production chain is: `evaluate_horn()` → `compileAttacks()` → `decisionProjection()`. Shadow harness (if present) validates the production path, not replaces it. The Lean theorem `certified_end_to_end_refinement` operates on canonical types, not shadow types.

---

## Test Verification

```
$ python -m pytest tests/spec/test_attack_compiler.py -v
8 passed
$ python -m pytest tests/spec/test_argument_compiler.py -v
5 passed
```

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Production attack path closes through canonical adapter | PASS |
| Shadow semantics not sole truth source | PASS |
| 13/13 argument+attack tests pass | PASS |
