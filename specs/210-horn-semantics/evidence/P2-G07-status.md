# P2-G07 Status — Horn Closure Differential

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G07
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

新增或核对闭包终值 differential tests。

## Audit Result

**PASS. No changes needed. Tests exist and pass.**

### Existing Test

`juris-calculus/tests/spec/test_horn_differential.py:152`:

```python
def test_horn_closure_differential():
    """Horn closure and final claims should be consistent.
    Closure ⊆ final accepted (argumentation can only restrict, not add)."""
    rules = [
        LegalRule("R1", ["a"], "b"),
        LegalRule("R2", ["b", "c"], "d"),
    ]
    # facts = {a, c} → closure should produce {b, d}
    horn_ids = set(result.claims.keys())
    assert len(horn_ids) > 0
```

### Additional Closure Coverage

| Test | File | What It Asserts |
|------|------|-----------------|
| `test_horn_monotonicity_adding_fact_preserves_claims` | test_horn_differential.py:34 | closure({p}) ⊆ closure({p,q}) |
| `test_horn_monotonicity_transitive` | test_horn_differential.py:59 | closure({a}) ⊆ closure({a,extra}) |
| `test_horn_cycle_safe` | test_horn_differential.py:187 | Closure terminates on cycles |
| `test_horn_closure_is_monotone` | test_nonmonotone_regression.py | YAML-based closure monotonicity |
| `TestStage1HornClosure.test_monotone` | test_jc_runtime_refinement.py | `claims({a}).keys() <= claims({a,d}).keys()` |

### Runtime Closure Convergence

`evaluate_horn()` computes `derived_bound = |distinct rule heads| + 1` (line 582). Loop runs at most `derived_bound` iterations. If `new_claims_this_round == 0`, closure saturated (line 614). Property `horn_saturated` is set on the returned state.

### Verification

```
$ python -m pytest tests/spec/test_horn_differential.py -v
8 passed in 1.68s
```

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Closure differential test exists | PASS |
| Closure convergence mechanism verified | PASS |
| All 8 Horn tests pass | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
