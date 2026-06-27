# P2-G01 Status — Define Inductive Horn Derivation

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 5.3, P2-G01
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

核对 `HornCanonical.lean`: `Derives` 必须是归纳关系，不得定义成"属于最终闭包"。

## Audit Result

**PASS. No changes needed.**

`HornCanonical.lean:81-85`:

```lean
inductive Derives (sys : HornSystem α) : α → Prop where
  | initial (a : α) (h : a ∈ sys.initialFacts) : Derives sys a
  | rule (r : HornRule α) (hr : r ∈ sys.rules)
      (premises_ok : ∀ p ∈ r.premises, Derives sys p) :
      Derives sys (r.conclusion)
```

`Derives` is an inductive type with two constructors:
- `initial`: base case from `sys.initialFacts`
- `rule`: inductive step — if all premises derive, conclusion derives

It is NOT defined as membership in the final closure (i.e., NOT `a ∈ hornClosure`). The soundness direction (`Derives → closure`) and completeness direction (`closure → Derives`) are proven separately as `derives_sound` and `derives_complete`.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Derives is `inductive`, not closure membership | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
