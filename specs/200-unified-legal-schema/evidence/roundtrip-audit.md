# P1-G06: Schema Round-Trip — Audit

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G06
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Does the Lean side use typed representation? Does the Python side achieve deterministic serialize/deserialize with zero field loss?

---

## Conclusion

**Both sides verified.** Lean uses typed IDs throughout canonical types; HornCanonical is polymorphic by design. Python achieves deterministic round-trip with zero field loss (6/6 tests pass).

---

## 1. Lean Side: Typed Representation

### 1.1 LegalSyntax.lean — All 12 canonical types use typed IDs

| Type | ID Field | Type Used |
|------|----------|-----------|
| LegalFact | `id` | `FactId` |
| LegalClaim | `id` | `ClaimId` |
| LegalRule | `id` | `RuleId` |
| LegalNorm | `id` | `NormId` |
| Defense | `id` | `DefenseId` (P1-G01 fix) |
| Priority | `id` | `PriorityId` (P1-G01 fix) |
| Violation | `id` | `ViolationId` (P1-G01 fix) |
| Reparation | `id` | `ReparationId` (P1-G01 fix) |
| Argument | `id` | `ArgumentId` |
| Attack | `id` | `AttackId` |
| Decision | `id` | `DecisionId` (P1-G01 fix) |
| Certificate | (no id field) | N/A |

### 1.2 HornCanonical.lean — Polymorphic, no bare String/Nat

HornCanonical is parameterized over `{α : Type} [DecidableEq α]`. It does NOT use bare `String` or `Nat` — it is generic over any decidable-eq type. Connection to typed IDs happens through instantiation (when `α = FactId`).

**8 blocking theorems, 0 sorry, 0 admit, 0 custom axiom:**

| Theorem | Status |
|---------|--------|
| `hornStep_monotone` | PROVEN |
| `hornClosure_extensive` | PROVEN |
| `hornClosure_closed` | PROVEN |
| `hornClosure_idempotent` | PROVEN |
| `derives_sound` | PROVEN |
| `derives_complete` | PROVEN |
| `hornClosure_least` | PROVEN |
| `horn_semantic_equivalence` | PROVEN |

### 1.3 Build Verification

```
$ lake build JurisLean.HornCanonical
Build completed successfully (2945 jobs).
```

---

## 2. Python Side: Deterministic Serialize/Deserialize

### 2.1 Round-Trip Tests (6/6 pass)

| Test | Assertion | Result |
|------|-----------|--------|
| `test_roundtrip_preserves_all_fields` | JSON → canonical → JSON: all fields preserved | PASS |
| `test_field_loss_count_zero` | Zero fields lost in round-trip | PASS |
| `test_id_conflation_count_zero` | No ID types conflated | PASS |
| `test_modality_preserved` | Enum values survive serialization | PASS |
| `test_interval_preserved` | TimeInterval survives round-trip | PASS |
| `test_model_hash_deterministic` | Same model → same SHA-256 hash | PASS |

### 2.2 Serialization Tests (8/8 pass)

| Test | Assertion | Result |
|------|-----------|--------|
| `test_aaf_round_trip` | AAF data survives serialization | PASS |
| `test_aaf_deterministic_output` | Same input → same JSON | PASS |
| `test_aaf_input_order_invariant` | Order-independent | PASS |
| `test_aaf_valid_json_structure` | Valid JSON output | PASS |
| `test_horn_round_trip` | Horn data survives serialization | PASS |
| `test_horn_deterministic_output` | Deterministic Horn output | PASS |
| `test_horn_valid_json_structure` | Valid JSON structure | PASS |
| `test_empty_inputs_round_trip` | Empty data survives round-trip | PASS |

---

## 3. Verdict

| Criterion | Result |
|-----------|--------|
| Lean side uses typed IDs (no bare String/Nat in canonical types) | **PASS** |
| Lean side builds cleanly | **PASS** (2945 jobs) |
| Python side deterministic serialize/deserialize | **PASS** (14/14 tests) |
| Round-trip zero field loss | **PASS** |
| Round-trip zero ID conflation | **PASS** |
| Modality enum preserved | **PASS** |
| TimeInterval preserved | **PASS** |
| Model hash deterministic | **PASS** |
| P1-G06 can be closed | **YES** |
