# SPEC-200 Requirements: Unified Legal Schema

## FREQ-200-001: Typed IDs
Model SHALL define distinct ID types:
`FactId`, `RuleId`, `NormId`, `ClaimId`, `ArgumentId`, `AttackId`, `SourceId`, `JurisdictionId`.

## FREQ-200-002: LegalRule ≠ LegalNorm
`LegalRule` and `LegalNorm` SHALL be different types.

## FREQ-200-003: Model Types
Model SHALL define:
`LegalFact`, `LegalClaim`, `LegalRule`, `LegalNorm`, `Defense`, `Priority`, `Violation`, `Reparation`, `Argument`, `Attack`, `Decision`, `Certificate`.

## FREQ-200-004: Modalities
Model SHALL define four modalities:
`OBLIGATION`, `PROHIBITION`, `PERMISSION`, `CONSTITUTIVE`.

## FREQ-200-005: Attack Kinds
Model SHALL define three attack kinds:
`REBUTTAL`, `EXCEPTION_DEFEAT`, `PRIORITY_DEFEAT`.

## FREQ-200-006: Reparation Modes
Model SHALL define four reparation modes:
`ALTERNATIVE`, `ORDERED_CHAIN`, `CONCURRENT`, `COURT_SELECTED`.

## FREQ-200-007: WellFormed
Model SHALL define `WellFormed` predicate covering:
- unique IDs
- valid rule references
- valid norm references
- valid defense references
- valid priority references
- valid attack endpoints
- valid source references
- valid temporal intervals
- valid jurisdiction references
- valid reparation structures

## RREQ-200-001: Canonical Adapters
JC SHALL provide explicit canonical adapters for LegalRule and LegalIRRule.

## RREQ-200-002: Round-Trip Field Preservation
Round-trip SHALL preserve every canonical field.

## SREQ-200-001: Unknown Schema Version
Unknown schema version SHALL fail closed.

## SREQ-200-002: Unknown Required Fields
Unknown required fields SHALL NOT be silently dropped.
