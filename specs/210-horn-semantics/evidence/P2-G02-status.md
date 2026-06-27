# P2-G02 Status — Prove Horn Derivation Soundness

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G02
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

核对 `derives_sound`: 若 `Derives sys a` 则 `a ∈ hornClosure`。

## Audit Result

**PASS. No changes needed.**

`HornCanonical.lean:93-110`:

```lean
theorem derives_sound {a : α} (h : Derives sys a) :
    a ∈ FiniteMonotoneSystem.iter (HornSystem.toFiniteMonotoneSystem sys)
      (Finset.card sys.univ) := by
```

- 0 sorry, 0 admit, 0 custom axiom
- Proof strategy: induction on `Derives`
  - `initial` case: uses `hornClosure_extensive`
  - `rule` case: premises ⊆ closure by IH, conclusion ∈ TH(closure), then `hornClosure_closed` folds it back

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| derives_sound proven (0 sorry) | PASS |
| Build verified | PASS (2945 jobs) |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
