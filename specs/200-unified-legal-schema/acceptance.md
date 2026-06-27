# SPEC-200 Acceptance Criteria

## AC-200-001: ID Types Defined
All 8 ID types exist as distinct Lean structures with `DecidableEq`.

## AC-200-002: Enums Defined
`Modality`, `AttackKind`, `ReparationMode` each have the correct number of constructors.

## AC-200-003: Model Types Defined
All 12 model types exist as Lean structures referencing the typed IDs.

## AC-200-004: LegalRule ≠ LegalNorm
`LegalRule` and `LegalNorm` are provably distinct types (cannot unify).

## AC-200-005: WellFormed Composed
`WellFormed` predicate exists and covers all 10 sub-conditions.

## AC-200-006: JSON Schema Valid
`legal-model.schema.json` validates correctly against JSON Schema Draft 7.

## AC-200-007: Canonical Adapter Field Preservation
Round-trip (canonical → JSON → canonical) preserves all fields with zero loss.

## AC-200-008: Unknown Version Fail-Closed
Passing an unknown `schema_version` to the adapter raises an error (not silent accept).

## AC-200-009: CI Gates Pass
```
lake build (Lean compiles with zero errors)
field_loss_count = 0
id_conflation_count = 0
unknown_version_acceptance_count = 0
```
