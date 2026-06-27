# P2-G05 Status — Remove Exceptions from JC Horn Stage

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G05
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

核对 `compiler_core/evaluator.py`: Horn stage 只做正推导，exception/priority/defeat 只出现在后续编译或 AAF 阶段。

## Audit Result

**PASS. No changes needed.**

### Architecture

`evaluator.py` provides two evaluation paths:

| Method | Stage | Monotone | Exceptions |
|--------|-------|----------|------------|
| `evaluate_horn()` (line 560) | Horn (Stage 1) | YES | NO |
| `evaluate()` (line 349) | Full (AAF stage) | NO | YES |

### Horn Stage Isolation

| Feature | `evaluate()` | `evaluate_horn()` |
|---------|-------------|-------------------|
| Exception chain penetration | Yes (line 268) | **No** |
| PROHIBITION blocking | Yes (line 256) | **No** |
| Rebuttal / confidence zeroing | Yes (line 435) | **No** |
| Constraint rules (force_state) | Yes (line 370, 456) | **No** |
| CriticalClarityFailure | Yes (line 482) | **No** |
| DDL modal gate | Yes (line 222) | **No** |
| Index used | `fact_to_rules` | `fact_to_rules_horn` |

### Index Construction (lines 116-127)

```python
self.fact_to_rules_horn: Dict[str, List[str]] = {}
for r in rules:
    for premise in r.premise_atoms:
        self.fact_to_rules_horn.setdefault(premise, []).append(r.id)
    for exception in r.exception_chain:
        # NOT added to fact_to_rules_horn
```

`fact_to_rules_horn` is built ONLY from `premise_atoms`. Exception atoms are excluded.

### `_apply_rule_horn()` (lines 511-558)

Retains: depth guard, premise check, `compute_formalizable`, claim construction.
Removes: exception chain, PROHIBITION, DDL modal gate, rebuttal, constraint rules.

### Monotonicity Guarantee

Claims in `evaluate_horn()` are only added, never removed (line 609: `claim.id not in state.claims`). Adding facts can only trigger more rules, never suppress existing claims.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Horn stage has no exception defeat | PASS |
| Horn stage has no PROHIBITION blocking | PASS |
| Horn stage has no rebuttal | PASS |
| Horn stage uses premises-only index | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
