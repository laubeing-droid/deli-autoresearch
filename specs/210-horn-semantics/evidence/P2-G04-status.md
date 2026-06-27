# P2-G04 Status — Prove Minimal Model Equivalence

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

核对 Horn 闭包与最小模型/最小不动点的一致关系。

## Audit Result

**PASS. No changes needed.**

Three theorems establish minimal model equivalence:

### 1. `hornClosure_closed` (lines 54-60)

```lean
theorem hornClosure_closed :
    HornSystem.TH sys (hornClosure) = hornClosure
```

Closure is a fixed point of TH. Delegates to `HornSystem.horn_result_fixed_point`.

### 2. `hornClosure_least` (lines 184-188)

```lean
theorem hornClosure_least {S : Finset α}
    (hS : HornSystem.TH sys S = S) :
    hornClosure ⊆ S
```

For any S closed under TH containing initialFacts, closure ⊆ S. Delegates to `horn_result_least_fixed_point`.

### 3. `horn_semantic_equivalence` (lines 196-200)

```lean
theorem horn_semantic_equivalence {a : α} :
    (a ∈ hornClosure) ↔ Derives sys a :=
  ⟨derives_complete sys, derives_sound sys⟩
```

Biconditional: inductive derivation ↔ closure membership.

### Summary

| Property | Theorem | Status |
|----------|---------|--------|
| Closure is fixed point | `hornClosure_closed` | PROVEN |
| Closure is least fixed point | `hornClosure_least` | PROVEN |
| Inductive ↔ closure | `horn_semantic_equivalence` | PROVEN |
| Closure is idempotent | `hornClosure_idempotent` | PROVEN |

All 0 sorry. Full build: 2945 jobs.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Minimal model equivalence proven | PASS |
| Build verified | PASS (2945 jobs) |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
