# SPEC-280 Requirements

## Goal

Compose all sealed components into the project's final end-to-end theorem: `certified_end_to_end_refinement`.

## Requirements (FREQ-280-001 through FREQ-280-007)

1. **R1** — `evaluate` SHALL compose canonical functions (compileAttacks → grounded → decisionProjection).
2. **R2** — Pipeline SHALL terminate on finite well-formed models.
3. **R3** — Checker acceptance SHALL imply formal output equality (accepted args → PROVED).
4. **R4** — Checker acceptance SHALL imply provenance safety.
5. **R5** — Checker acceptance SHALL imply temporal safety.
6. **R6** — Checker acceptance SHALL imply jurisdiction safety.
7. **R7** — Final theorem SHALL NOT assume its conclusion.

## Blocking status

`certified_end_to_end_refinement` is on the **blocking path**. ZERO sorry tolerance.

## Composed components

| Component | SPEC | Theorem |
|-----------|------|---------|
| Checker soundness | 250 | check_sound |
| Certificate verification | 250 | certificate_verifies |
| Provenance safety | 270 | provenance_sound |
| Temporal safety | 270 | temporal_safe |
| Jurisdiction safety | 270 | jurisdiction_safe |
| Decision projection | 240 | decisionProjection |
| Attack compilation | 240 | compileAttacks |
