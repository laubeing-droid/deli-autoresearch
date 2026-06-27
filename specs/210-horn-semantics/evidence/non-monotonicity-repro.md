# P0-G03: Horn Non-Monotonicity — Reproduction Report

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G03
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Does `evaluate_horn()` in `juris-calculus/compiler_core/evaluator.py` mix exception/priority/negative effects into the Horn stage, breaking monotonicity?

---

## Conclusion

**Risk eliminated.** The current `evaluate_horn()` implementation is strictly monotone. It does NOT execute exception chains, PROHIBITION blocking, rebuttal, or constraint rules. Five dedicated test functions across two test suites directly verify this property.

---

## 1. Code Path Analysis

### 1.1 Horn Index Construction (lines 116-127)

```python
# fact_to_rules includes exception atoms (for evaluate())
self.fact_to_rules: Dict[str, List[str]] = {}
# fact_to_rules_horn excludes exception atoms (for evaluate_horn())
self.fact_to_rules_horn: Dict[str, List[str]] = {}
for r in rules:
    for premise in r.premise_atoms:
        self.fact_to_rules.setdefault(premise, []).append(r.id)
        self.fact_to_rules_horn.setdefault(premise, []).append(r.id)
    for exception in r.exception_chain:
        self.fact_to_rules.setdefault(exception, []).append(r.id)
        # NOT added to fact_to_rules_horn
```

**Key**: `fact_to_rules_horn` is built ONLY from `premise_atoms`, never from `exception_chain`. This means rule triggering in the Horn stage is based purely on positive premises.

### 1.2 `evaluate_horn()` (lines 560-630)

| Feature | `evaluate()` | `evaluate_horn()` |
|---------|-------------|-------------------|
| Exception chain penetration | Yes (line 268-281) | **No** |
| PROHIBITION blocking | Yes (line 256-265) | **No** |
| Rebuttal / confidence zeroing | Yes (line 435-453) | **No** |
| Constraint rules (force_state) | Yes (line 370-391, 456-480) | **No** |
| CriticalClarityFailure | Yes (line 482-498) | **No** |
| DDL modal gate | Yes (line 222-265) | **No** |
| Claims only added, never removed | No (rebuttal can zero confidence) | **Yes** |
| Index used | `fact_to_rules` | `fact_to_rules_horn` |

### 1.3 `_apply_rule_horn()` (lines 511-558)

Stripped-down rule application. Retains:
- Depth guard (`depth > k_max`)
- Premise check
- `compute_formalizable` scoring
- Claim construction

Removes:
- Exception chain penetration
- PROHIBITION blocking
- DDL modal gate (OBLIGATION/PROHIBITION/PERMISSION)
- Rebuttal hook
- Constraint rules

### 1.4 `compute_formalizable` scoring (lines 36-68)

This function is shared between `evaluate()` and `evaluate_horn()`. It affects **confidence** (a floating-point score), not **claim presence**. A claim with low confidence is still produced; it is never removed. Therefore `compute_formalizable` does not break monotonicity of the claim set.

**Monotonicity argument**: If `F ⊆ G` (facts), then every rule triggered by `F` is also triggered by `G`. `_apply_rule_horn` produces at most one claim per rule. Claims are never removed. Therefore `claims(F) ⊆ claims(G)`.

---

## 2. Attempted Counterexample

### 2.1 Original Risk (Historical)

The original non-monotonicity concern was: "Horn stage mixes in exception/priority/negative effects, so adding a fact could remove an existing claim."

### 2.2 Constructed Test Case

```
Rules:
  R1: p → h        (exception_chain: [R_exc])
  R_exc: q → ¬h    (would defeat h if exceptions were applied)

Facts A: {p}
Facts B: {p, q}     (superset of A)
```

**Expected if non-monotone**: `claims(A) = {h}`, `claims(B) = {}` (h defeated by exception).

**Actual with `evaluate_horn()`**:
- `claims(A) = {h}` — R1 fires because p is present
- `claims(B) = {h}` — R1 fires because p is present; R_exc is NOT triggered because `fact_to_rules_horn` does not include exception atoms, so `q` only triggers rules where it appears as a `premise_atom`, not as an exception trigger.

**Result**: `claims(A) ⊆ claims(B)` — monotonicity holds.

### 2.3 Rebuttal Case

```
Rules:
  R1: a → b
  R_rebut: c → not_b   (rebuttal rule)

Facts: {a, c}
```

**Expected if non-monotone**: b would be zeroed by rebuttal.

**Actual with `evaluate_horn()`**: `claims = {b}` — rebuttal is not executed in Horn stage.

**Result**: Monotonicity holds. Rebuttal only applies in `evaluate()`.

---

## 3. Test Coverage

### 3.1 Direct Monotonicity Tests (5 functions)

| Test | File:Line | What It Asserts |
|------|-----------|-----------------|
| `test_horn_monotonicity_adding_fact_preserves_claims` | test_horn_differential.py:34 | `claims({p}) ⊆ claims({p, q})` even with exception chain |
| `test_horn_monotonicity_transitive` | test_horn_differential.py:59 | 3-rule chain: `claims({a}) ⊆ claims({a, extra})` |
| `test_horn_closure_is_monotone` | test_nonmonotone_regression.py:47 | YAML rules with exception chains: monotone |
| `TestStage1HornClosure.test_monotone` | test_jc_runtime_refinement.py:42 | `claims({a}).keys() <= claims({a, d}).keys()` |
| `test_horn_eval_independent_of_time` | test_safety_theorems.py:42 | Horn closure positive-only, no temporal invalidation |

### 3.2 Exception Defeat Tests (2 functions)

| Test | File:Line | What It Asserts |
|------|-----------|-----------------|
| `test_horn_no_exception_defeat` | test_horn_differential.py:88 | Exception in `exception_chain` does NOT defeat claim in Horn stage |
| `test_horn_no_rebuttal` | test_horn_differential.py:110 | Rebuttal rule does NOT suppress claim in Horn stage |

### 3.3 Additional Horn Tests (6 functions)

| Test | File:Line | What It Asserts |
|------|-----------|-----------------|
| `test_horn_single_step_differential` | test_horn_differential.py:130 | Two-step chain produces both claims |
| `test_horn_closure_differential` | test_horn_differential.py:152 | Closure produces at least 1 claim |
| `test_horn_empty_facts` | test_horn_differential.py:176 | No facts → no claims |
| `test_horn_cycle_safe` | test_horn_differential.py:187 | Cyclic rules terminate |
| `TestStage1HornClosure.test_positive_only` | test_jc_runtime_refinement.py:59 | No negative premises in Horn |
| `test_temporal_safety` | test_end_to_end.py:112 | Monotone, positive Horn |

### 3.4 Test Verdict

All 8 Horn differential tests pass. All 2 JC runtime Stage 1 tests pass. All 12 safety theorem tests pass. All 15 end-to-end tests pass.

---

## 4. Remaining Risks

### 4.1 Low Risk: `compute_formalizable` depth guard

`_apply_rule_horn` returns `None` if `depth > self.config.k_max` (line 522). In theory, if `k_max` were dynamically adjusted between calls, this could break monotonicity. In practice, `k_max` is set once at `DomainConfig` construction and never modified. **Risk: negligible.**

### 4.2 Low Risk: `state.rules_applied` deduplication

`evaluate_horn` skips rules already in `state.rules_applied` (line 605). If a caller reuses state across multiple `evaluate_horn` calls, claims from the first call prevent re-derivation. This is by-design deduplication, not non-monotonicity. **Risk: none.**

### 4.3 No Risk: `fact_to_rules_horn` construction

The Horn index is built once at `__init__` and never mutated. It consistently excludes exception atoms. **Risk: none.**

---

## 5. Comparison: `evaluate()` vs `evaluate_horn()`

| Property | `evaluate()` | `evaluate_horn()` |
|----------|-------------|-------------------|
| Monotone | **No** (rebuttal, PROHIBITION can remove/zero claims) | **Yes** |
| Positive | **No** (exceptions, blocking) | **Yes** |
| Terminates | **Yes** (max_iterations) | **Yes** (derived_bound from rule heads) |
| Trust boundary | Empirical (E) | Empirical, but Lean-proven monotone (F+S) |

The full `evaluate()` is intentionally non-monotone — that's the argumentation stage. The Horn stage (`evaluate_horn()`) is the monotone core that feeds into the Lean-proven `HornFixedPoint` and `HornCanonical` theorems.

---

## 6. Verdict

| Criterion | Result |
|-----------|--------|
| Horn stage mixes exceptions? | **NO** — `fact_to_rules_horn` excludes exception atoms |
| Horn stage has PROHIBITION? | **NO** — not in `_apply_rule_horn` |
| Horn stage has rebuttal? | **NO** — not in `_apply_rule_horn` |
| Horn stage has constraint rules? | **NO** — not in `evaluate_horn` |
| Adding a fact can remove a claim? | **NO** — claims only added, never removed |
| Minimal counterexample exists? | **NO** — all attempts produce monotone results |
| Test coverage adequate? | **YES** — 5 monotone + 2 exception-defeat tests |
| P0-G03 can be closed? | **YES** — non-monotonicity risk is eliminated |

The Horn stage is strictly monotone. The original risk described in Playbook E ("Horn stage may still mix in exception/priority/negative effect") does not apply to the current codebase.
