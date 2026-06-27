# P3-G04 Status — Formalize Defenses and Burdens

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 6.3, P3-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

defense / burden 语义不能只存在于运行时注释层。

## Audit Result

**PASS. No fix needed.**

### DefenseApplicable (DDLDefinitions.lean:93-95)

```lean
def DefenseApplicable (m : LegalModel) (d : Defense) : Prop :=
  d.target ∈ (m.rules.map (fun r => r.id)).toFinset
  ∧ ∀ rf ∈ d.facts_required, rf ∈ (m.facts.map (fun f => f.id)).toFinset
```

Defense applicability requires: target rule exists, all required facts present.

### BurdenSatisfied (DDLDefinitions.lean:99-100)

```lean
def BurdenSatisfied (m : LegalModel) (d : Defense) : Prop :=
  d.burden_of_proof = "" ∨ ∀ rf ∈ d.facts_required, rf ∈ (m.facts.map (fun f => f.id)).toFinset
```

Empty burden = no additional proof needed. Non-empty = all required facts must be present.

### Theorem: burden_unsatisfied_blocks_defense (lines 153-162)

```lean
theorem burden_unsatisfied_blocks_defense
    (m : LegalModel) (d : Defense)
    (h_not_burden : ¬ BurdenSatisfied m d) :
    ¬ DefenseApplicable m d
```

Fully proven (0 sorry). If burden is not satisfied, defense is not applicable. This is a blocking-path theorem, listed in SORRY_LEDGER.md as proven.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| DefenseApplicable is a semantic predicate | PASS |
| BurdenSatisfied is a semantic predicate | PASS |
| burden_unsatisfied_blocks_defense proven (0 sorry) | PASS |
| Not just runtime comments | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
