# Axiom Report — Unified Legal Kernel v1

Generated: 2026-06-27

## Standard Lean Axioms Used

| Axiom | Usage |
|-------|-------|
| `propext` | Propositional extensionality (Mathlib) |
| `Quot.sound` | Quotient soundness (Mathlib) |
| `Classical.choice` | Classical logic (Mathlib) |

## Custom Axioms

**NONE.** Zero custom axioms in the Unified Legal Kernel.

## Verification

```bash
cd legal-math-modeling/proofs/lean/juris_lean
lake build +JurisLean.AxiomAudit
```

Actual output (2026-06-27):

```
info: JurisLean/AxiomAudit.lean:9:0: 'FiniteMonotoneSystem.exists_fixpoint_le_card' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:10:0: 'FiniteMonotoneSystem.fixed_at_card' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:13:0: 'DungAAF.grounded_is_least_fixed_point' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:16:0: 'HornSystem.horn_completeness' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:17:0: 'HornSystem.horn_result_is_minimal_model' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:19:0: 'weightedSupDist_complete' depends on axioms: [propext, Classical.choice, Quot.sound]
Build completed successfully (2960 jobs).
```

**Conclusion**: Only `propext`, `Classical.choice`, `Quot.sound` — all standard Lean 4 / Mathlib axioms. Zero custom axioms.
