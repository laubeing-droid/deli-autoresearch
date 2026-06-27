# P2-G06 Status — Horn Single-Step Differential

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G06
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

新增或核对单步推导 differential tests。

## Audit Result

**PASS. No changes needed. Tests exist and pass.**

### Existing Test

`juris-calculus/tests/spec/test_horn_differential.py:130`:

```python
def test_horn_single_step_differential():
    """Each iteration produces only NEW claims (differential)."""
    rules = [
        LegalRule("R1", ["a"], "b"),
        LegalRule("R2", ["b"], "c"),
    ]
    # ... a → b → c two-step chain
    assert "b" in result.claims
    assert "c" in result.claims
```

### Additional Single-Step Coverage

| Test | File | What It Asserts |
|------|------|-----------------|
| `test_horn_monotonicity_adding_fact_preserves_claims` | test_horn_differential.py:34 | Adding q preserves h (monotone) |
| `test_horn_monotonicity_transitive` | test_horn_differential.py:59 | Transitive chain: a→b→c→d |
| `test_horn_no_exception_defeat` | test_horn_differential.py:88 | Exception does NOT suppress claim |
| `test_horn_no_rebuttal` | test_horn_differential.py:110 | Rebuttal does NOT suppress claim |
| `test_horn_empty_facts` | test_horn_differential.py:176 | No facts → no claims |
| `test_horn_cycle_safe` | test_horn_differential.py:187 | Cyclic rules terminate |

### Verification

```
$ python -m pytest tests/spec/test_horn_differential.py -v
8 passed in 1.68s
```

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Single-step differential test exists | PASS |
| All 8 Horn tests pass | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
