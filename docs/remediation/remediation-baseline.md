# Remediation Baseline: Cross-Repo Math Proof → Engineering Capability

**Created**: 2026-06-23
**Base Commits**: deli-autoresearch=8ad45ec, juris-calculus=ab2ac6f, legal-math-modeling=2a0bbc6
**Final Commits**: deli-autoresearch=4b7ca22, juris-calculus=a06eea4, legal-math-modeling=c111c47

## Reclassification Results

| Item | Original | Reclassified |
|------|----------|-------------|
| F_monotone | CONFIRMED | INCOMPLETE (sorry) |
| iteration_monotone | CONFIRMED | EVASION (returns True) |
| finite_termination | CONFIRMED | INCOMPLETE |
| iteration_bound | CONFIRMED | INCOMPLETE |
| grounded_is_fixed_point | CONFIRMED | INCOMPLETE |
| grounded_is_least_fixed_point | CONFIRMED | INCOMPLETE |
| grounded_is_least_complete | CONFIRMED | INCOMPLETE |
| grounded_unique | CONFIRMED | INCOMPLETE |
| labelling_partition | CONFIRMED | INCOMPLETE |
| in_soundness | CONFIRMED | INCOMPLETE |
| out_soundness | CONFIRMED | INCOMPLETE |
| undecided_characterization | CONFIRMED | INCOMPLETE |
| self_attack_undecided | CONFIRMED | INCOMPLETE |
| G8 Horn truncation | CONFIRMED | PARTIAL (only wrapper detects) |
| Deli-juris interface | CONFIRMED | UNINTEGRATED (missing fields) |
| Universal SMT | CONFIRMED | BOUNDED_ONLY (N=2..13) |
| Golden corpus | CONFIRMED | SPEC_ONLY (schema, no execution) |
| DAG SCC | CONFIRMED | KNOWN_FAILURE (test skipped) |
| Cross-repo tests | Implied | UNINTEGRATED (0 tests) |
| Lean→Python refinement | Planned | UNINTEGRATED (never started) |
| B breakthrough | CONFIRMED | BOUNDED_ONLY (Z3 N<=10 only) |
| J breakthrough | CONFIRMED | PARTIAL (CN→US one direction) |

## Repair Summary (R0-R5)

| Phase | Repo | Changes | Status |
|-------|------|---------|--------|
| R0 | deli-auto | remediation-baseline.md, freeze | Committed |
| R1 | deli-auto | bridge v3.0 fields, fail-closed, cross-repo tests | Committed |
| R1 | legal-math | lean_manifest.json | Committed |
| R2 | juris-calc | evaluate_horn derived bound, IRState fields | Committed |
| R3 | legal-math | theorem-proofs.md (13 complete math proofs) | Committed |
| R4 | deli-auto | aaf_canonical.py, certificate_verifier.py | Committed |
| R5 | juris-calc | golden corpus 9 cases, SMT cleanup, B/J downgrade | Committed |