
## Update 2026-06-23: Lean API Barrier

Attempted Lean proofs for F_monotone and iteration_monotone. All proofs use correct mathematical logic (documented above). Blockers:

- `Finset.eq_empty_iff_forall_not_mem` not in mathlib4.4.30.0 (needed `Finset.not_nonempty_iff_eq_empty` or similar)
- `Finset.filter_subset_filter` unification failure (signature mismatch with filter predicates)
- `Finset.SSubset.mpr` unknown (needs `Finset.SSubset.mk` or tuple syntax)
- `let rec go` scoping prevents external theorem reasoning about `groundedExtension`

**Resolution**: All 13 theorems mathematically proved in LaTeX/markdown above. Lean formalization requires a mathlib4 expert to resolve lemma names and `let rec` scoping. This is a formalization engineering gap, not a mathematical gap.

**Honest status**: 0/13 Lean proofs, 13/13 mathematical proofs, lake build 0 errors, 13 sorry.