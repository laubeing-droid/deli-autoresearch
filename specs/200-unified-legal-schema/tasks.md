# SPEC-200 Tasks: Unified Legal Schema

## Lean Formalization

- [x] TASK-200-001: Define typed IDs (FactId, RuleId, NormId, ClaimId, ArgumentId, AttackId, SourceId, JurisdictionId)
- [x] TASK-200-002: Prove ID decidable equality
- [x] TASK-200-003: Define modality and rule enums (Modality, AttackKind, ReparationMode)
- [x] TASK-200-004: Define LegalFact
- [x] TASK-200-005: Define LegalClaim
- [x] TASK-200-006: Define LegalRule
- [x] TASK-200-007: Define LegalNorm (distinct from LegalRule)
- [x] TASK-200-008: Define Defense and Burden
- [x] TASK-200-009: Define Violation
- [x] TASK-200-010: Define Reparation
- [x] TASK-200-011: Define Argument with derivation witness
- [x] TASK-200-012: Define Attack
- [x] TASK-200-013: Define Decision
- [x] TASK-200-014: Define Certificate
- [x] TASK-200-015: Define LegalModel aggregate
- [x] TASK-200-016: Define WellFormedIds
- [x] TASK-200-017: Define WellFormedReferences
- [x] TASK-200-018: Define WellFormedTemporal
- [x] TASK-200-019: Define WellFormedJurisdiction
- [x] TASK-200-020: Define WellFormedReparation
- [x] TASK-200-021: Compose WellFormed predicate
- [x] TASK-200-022: Prove reference-existence lemmas

## JSON Schema

- [x] TASK-200-023: Define canonical JSON schema (legal-model.schema.json)
- [x] TASK-200-024: Define certificate schema (certificate.schema.json)

## JC Adapters

- [x] TASK-200-025: Implement canonical_schema.py (Pydantic models)
- [x] TASK-200-026: Implement canonical_adapter.py (LegalRule + LegalIRRule adapters)
- [x] TASK-200-027: Add YAML adapter
- [x] TASK-200-028: Add round-trip property tests
- [x] TASK-200-029: Add schema-version negative tests

## Red Team

- [x] TASK-200-030: Red-team field preservation
