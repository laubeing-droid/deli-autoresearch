# P1-G03: WellFormed Legal Model — Audit

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G03
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Does `LegalWellFormed.lean` enforce ID uniqueness, reference closure, and jurisdiction/temporal constraints for all canonical types?

---

## Conclusion

**One gap found and fixed.** `WellFormedIds` covered 6 of 12 component types for ID uniqueness. Added 5 missing uniqueness constraints (defenses, priorities, violations, reparations, decisions). All reference closure and temporal/jurisdiction constraints were already complete.

---

## 1. Before State

### 1.1 WellFormedIds (before fix)

| Component | Uniqueness Enforced | Status |
|-----------|-------------------|--------|
| facts | `facts_unique` | OK |
| rules | `rules_unique` | OK |
| norms | `norms_unique` | OK |
| claims | `claims_unique` | OK |
| arguments | `arguments_unique` | OK |
| attacks | `attacks_unique` | OK |
| defenses | — | **MISSING** |
| priorities | — | **MISSING** |
| violations | — | **MISSING** |
| reparations | — | **MISSING** |
| decisions | — | **MISSING** |
| certificates | — | Not applicable (no single-ID structure) |

### 1.2 Reference Closure (before fix — already complete)

| Predicate | References Checked | Status |
|-----------|-------------------|--------|
| `WellFormedRuleRefs` | premises→FactId, conclusion→FactId, source→SourceId, jurisdiction→JurisdictionId | OK |
| `WellFormedNormRefs` | condition→FactId, source→SourceId, jurisdiction→JurisdictionId | OK |
| `WellFormedDefenseRefs` | target→RuleId, facts_required→FactId | OK |
| `WellFormedPriorityRefs` | higher→RuleId, lower→RuleId | OK |
| `WellFormedAttackRefs` | attacker→ArgumentId, target→ArgumentId | OK |
| `WellFormedArgumentRefs` | claim→ClaimId, rule→RuleId, support_facts→FactId, sources→SourceId | OK |
| `WellFormedViolationRefs` | rule→RuleId, trigger_fact→FactId | OK |
| `WellFormedReparation` | target_violation→ViolationId (via existence check) | OK |

### 1.3 Temporal/Jurisdiction (before fix — already complete)

| Predicate | Constraints | Status |
|-----------|-------------|--------|
| `WellFormedTemporal` | rules: start ≤ end_, norms: start ≤ end_ | OK |
| `WellFormedJurisdiction` | rules: jurisdiction exists, norms: jurisdiction exists | OK |

---

## 2. Fix Applied

Added 5 fields to `WellFormedIds`:

```lean
structure WellFormedIds (M : LegalModel) : Prop where
  -- existing 6
  facts_unique : M.facts.Pairwise (fun a b => a.id ≠ b.id)
  rules_unique : M.rules.Pairwise (fun a b => a.id ≠ b.id)
  norms_unique : M.norms.Pairwise (fun a b => a.id ≠ b.id)
  claims_unique : M.claims.Pairwise (fun a b => a.id ≠ b.id)
  arguments_unique : M.arguments.Pairwise (fun a b => a.id ≠ b.id)
  attacks_unique : M.attacks.Pairwise (fun a b => a.id ≠ b.id)
  -- NEW 5
  defenses_unique : M.defenses.Pairwise (fun a b => a.id ≠ b.id)
  priorities_unique : M.priorities.Pairwise (fun a b => a.id ≠ b.id)
  violations_unique : M.violations.Pairwise (fun a b => a.id ≠ b.id)
  reparations_unique : M.reparations.Pairwise (fun a b => a.id ≠ b.id)
  decisions_unique : M.decisions.Pairwise (fun a b => a.id ≠ b.id)
```

**Note**: `certificates` excluded — `Certificate` has no `id` field; uniqueness is by content (model_hash + input_hash + decision).

---

## 3. Build Verification

```
$ lake build JurisLean.LegalWellFormed JurisLean.EndToEnd
Build completed successfully (2952 jobs).
```

Pre-existing warnings only (DungFixedPoint unused variable, EndToEnd unused variable). No new errors.

### 3.1 Downstream Impact

| Module | Uses WellFormedIds directly? | Affected? |
|--------|------------------------------|-----------|
| `EndToEnd.lean` | Imports LegalWellFormed but does not construct WellFormedIds | NO |
| `SafetyTheorems.lean` | Does not import LegalWellFormed | NO |
| `DDLDefinitions.lean` | Does not import LegalWellFormed | NO |
| `AttackDecision.lean` | Does not import LegalWellFormed | NO |
| `CertificateChecker.lean` | Does not import LegalWellFormed | NO |

No module constructs `WellFormedIds` or `WellFormed` values directly — all use them as `Prop` (proof obligations), so adding fields is backward-compatible.

---

## 4. Completeness Matrix

### 4.1 Playbook P1-G03 Checklist

| Checkpoint | Status | Evidence |
|------------|--------|----------|
| ID 唯一性 — all 12 components | **PASS** (after fix) | `WellFormedIds` with 11 Pairwise constraints (certificates excluded) |
| 引用闭合 — rules→facts | **PASS** | `WellFormedRuleRefs` |
| 引用闭合 — norms→facts | **PASS** | `WellFormedNormRefs` |
| 引用闭合 — defenses→rules/facts | **PASS** | `WellFormedDefenseRefs` |
| 引用闭合 — priorities→rules | **PASS** | `WellFormedPriorityRefs` |
| 引用闭合 — attacks→arguments | **PASS** | `WellFormedAttackRefs` |
| 引用闭合 — arguments→claims/rules/facts/sources | **PASS** | `WellFormedArgumentRefs` |
| 引用闭合 — violations→rules/facts | **PASS** | `WellFormedViolationRefs` |
| 引用闭合 — reparations→violations | **PASS** | `WellFormedReparation` |
| jurisdiction 字段合法性 | **PASS** | `WellFormedJurisdiction` |
| temporal 字段合法性 | **PASS** | `WellFormedTemporal` |

### 4.2 Composed WellFormed Structure

```lean
structure WellFormed (M : LegalModel) : Prop where
  ids_unique : WellFormedIds M         -- now 11 constraints
  rule_refs : WellFormedRuleRefs M
  norm_refs : WellFormedNormRefs M
  defense_refs : WellFormedDefenseRefs M
  priority_refs : WellFormedPriorityRefs M
  attack_refs : WellFormedAttackRefs M
  argument_refs : WellFormedArgumentRefs M
  temporal : WellFormedTemporal M
  jurisdiction : WellFormedJurisdiction M
  reparation : WellFormedReparation M
  violation_refs : WellFormedViolationRefs M
```

11 sub-predicates, unchanged structure.

---

## 5. Remaining Issues (Out of P1-G03 Scope)

| Issue | Severity | Notes |
|-------|----------|-------|
| `WellFormedTemporal` does not check `LegalFact.time` | Low | Fact timestamps are observational, not validity intervals |
| `WellFormedReparation` does not validate `ordered_successors` existence | Low | Only checks non-emptiness for ORDERED_CHAIN mode |
| Certificates not uniqueness-checked | N/A | No `id` field on Certificate |

---

## 6. Verdict

| Criterion | Result |
|-----------|--------|
| ID uniqueness for all components | **PASS** (after adding 5 constraints) |
| Reference closure complete | **PASS** (was already complete) |
| Temporal constraints present | **PASS** (rules + norms) |
| Jurisdiction constraints present | **PASS** (rules + norms) |
| Build passes | **PASS** (2952 jobs, 0 new errors) |
| No new sorry/admit | **PASS** |
| P1-G03 can be closed | **YES** |
