# SPEC-200 Design: Unified Legal Schema

## Architecture

The canonical legal schema defines the ground truth data model shared across:
- **Lean formalization** (JurisLean): typed structures with decidable equality
- **JSON schema** (schemas/): machine-readable validation
- **JC runtime** (juris-calculus): canonical adapter layer

## Module Layout

### Lean (legal-math-modeling)
```
JurisLean/LegalIds.lean      — 8 typed IDs with DecidableEq
JurisLean/LegalSyntax.lean   — 12 canonical model types + enums
JurisLean/LegalModel.lean    — LegalModel aggregate + composition
JurisLean/LegalWellFormed.lean — WellFormed predicate suite
```

### JSON Schema (juris-calculus)
```
schemas/legal-model.schema.json  — Full model validation
schemas/certificate.schema.json  — Certificate validation
```

### Runtime Adapters (juris-calculus)
```
compiler_core/canonical_schema.py    — Pydantic models + validation
compiler_core/canonical_adapter.py   — round-trip adapters
```

## Data Model

### ID Types (all opaque wrappers over String)
- FactId, RuleId, NormId, ClaimId, ArgumentId, AttackId, SourceId, JurisdictionId

### Enums
- Modality: OBLIGATION | PROHIBITION | PERMISSION | CONSTITUTIVE
- AttackKind: REBUTTAL | EXCEPTION_DEFEAT | PRIORITY_DEFEAT
- ReparationMode: ALTERNATIVE | ORDERED_CHAIN | CONCURRENT | COURT_SELECTED

### Core Types
- LegalFact: id + content + source + temporal
- LegalClaim: id + content + claimant
- LegalRule: id + modality + condition + consequence + source + jurisdiction
- LegalNorm: id + condition + consequence + source (≠ LegalRule)
- Defense: id + kind + target + burden
- Priority: id + higher + lower
- Violation: id + rule + fact + support
- Reparation: id + mode + target + ordered_successors
- Argument: id + claim + rule + support_facts + sources + witness
- Attack: id + kind + attacker_id + target_id
- Decision: id + status + arguments + attacks
- Certificate: model_hash + input_hash + decision + derivation_witnesses

## Dependency Order
1. LegalIds (no deps)
2. LegalSyntax (depends on LegalIds)
3. LegalModel (depends on LegalSyntax)
4. LegalWellFormed (depends on LegalModel)
5. JSON Schema (parallel with Lean)
6. Adapters (depends on JSON Schema + runtime)
7. Round-trip tests (depends on adapters)
