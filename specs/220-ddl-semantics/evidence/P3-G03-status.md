# P3-G03 Status — Formalize Violation Semantics

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 6.3, P3-G03
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

violation 不能仅作为字符串标签，必须进入规范语义。

## Audit Result

**PASS. No fix needed.**

### ViolationValid (DDLDefinitions.lean:82-86)

```lean
def ViolationValid (m : LegalModel) (v : Violation) : Prop :=
  v.rule ∈ (m.rules.map (fun r => r.id)).toFinset
  ∧ v.trigger_fact ∈ (m.facts.map (fun f => f.id)).toFinset
  ∧ ∀ sf ∈ v.support_facts, sf ∈ (m.facts.map (fun f => f.id)).toFinset
  ∧ v.trigger_fact ∈ v.support_facts
```

Four conditions for a violation to be valid:
1. The violated rule exists in `m.rules`
2. The trigger fact exists in `m.facts`
3. All support facts exist in `m.facts`
4. The trigger fact is itself a support fact

This is a semantic predicate (Prop), not a string label. The Violation type in LegalSyntax.lean uses typed `RuleId` and `FactId`, not bare strings.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| ViolationValid is a semantic predicate | PASS |
| References typed IDs (RuleId, FactId) | PASS |
| Rule existence check | PASS |
| Trigger/support fact existence check | PASS |
| No code changes required | PASS |

---

## Allowed Modifications

None. Audit only.
