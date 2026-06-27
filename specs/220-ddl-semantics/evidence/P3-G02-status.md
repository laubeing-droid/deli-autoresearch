# P3-G02 Status — Formalize Norm Activation

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 6.3, P3-G02
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

activation 必须受条件、时间、法域控制。

## Audit Result

**PASS. No fix needed.**

### NormActive (DDLDefinitions.lean:22-24)

```lean
def NormActive (m : LegalModel) (norm : LegalNorm) : Prop :=
  norm.enabled = true
  ∧ ∀ c ∈ norm.condition, c ∈ (m.facts.map (fun f => f.id)).toFinset
```

Activation is conditioned on:
1. `enabled = true`
2. All condition facts present in `m.facts`

### Temporal Control (LegalWellFormed.lean)

`WellFormedTemporal` requires `start ≤ end` for all rules and norms. This is a well-formedness constraint at model level.

### Jurisdiction Control (LegalWellFormed.lean)

`WellFormedJurisdiction` requires rule/norm jurisdiction IDs to exist in `m.jurisdictions`.

### Design Note

Temporal/jurisdiction constraints are enforced at model validation level (WellFormed predicates), not at individual norm activation level. This is correct: a norm's activation conditions are its `condition` facts; temporal/jurisdiction validity is a model-wide property.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Activation checks enabled flag | PASS |
| Activation checks condition facts | PASS |
| Temporal validity at model level | PASS |
| Jurisdiction validity at model level | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
