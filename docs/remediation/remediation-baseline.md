 # Remediation Baseline: Cross-Repo Math Proof → Engineering Capability

 **Created**: 2026-06-23
 **Base Commits**: deli-autoresearch=8ad45ec, juris-calculus=ab2ac6f, legal-math-modeling=2a0bbc6
 **Audit Source**: `D:\cross_repo_audit_report.md`

 ---

 ## 1. Reclassification of Claims

 Every item from the previous round's audit that was marked CONFIRMED but does not survive strict scrutiny is reclassified below.

 ### 1.1 Lean Theorems (legal-math-modeling, proofs/lean/juris_lean/JurisLean/DungAAF.lean)

 | # | Theorem | Claimed Status | Actual Status | Category | Evidence |
 |---|---------|---------------|---------------|----------|----------|
 | 1 | F_monotone | CONFIRMED | `sorry` at line 45 | INCOMPLETE | DungAAF.lean:44-45 |
 | 2 | iteration_monotone | CONFIRMED | Returns `True` at line 47, NOT the monotonic inclusion `iter k ∅ ⊆ iter (k+1) ∅` | EVASION | DungAAF.lean:47-48 |
 | 3 | finite_termination | CONFIRMED | `sorry` at line 51 | INCOMPLETE | DungAAF.lean:50-51 |
 | 4 | iteration_bound | CONFIRMED | `sorry` at line 54 | INCOMPLETE | DungAAF.lean:53-54 |
 | 5 | grounded_is_fixed_point | CONFIRMED | `sorry` at line 57 | INCOMPLETE | DungAAF.lean:56-57 |
 | 6 | grounded_is_least_fixed_point | CONFIRMED | `sorry` at line 61 | INCOMPLETE | DungAAF.lean:59-61 |
 | 7 | grounded_is_least_complete | CONFIRMED | `sorry` at line 65 | INCOMPLETE | DungAAF.lean:63-65 |
 | 8 | grounded_unique | CONFIRMED | `sorry` at line 68 | INCOMPLETE | DungAAF.lean:67-68 |
 | 9 | labelling_partition | CONFIRMED | `sorry` at line 73 | INCOMPLETE | DungAAF.lean:70-73 |
 | 10 | in_soundness | CONFIRMED | `sorry` at line 77 | INCOMPLETE | DungAAF.lean:75-77 |
 | 11 | out_soundness | CONFIRMED | `sorry` at line 81 | INCOMPLETE | DungAAF.lean:79-81 |
 | 12 | undecided_characterization | CONFIRMED | `sorry` at line 85 | INCOMPLETE | DungAAF.lean:83-85 |
 | 13 | self_attack_undecided | CONFIRMED | `sorry` at line 89 | INCOMPLETE | DungAAF.lean:87-89 |

 **Summary**: 12 INCOMPLETE + 1 EVASION = 0/13 complete.

 ### 1.2 Engineering Items

 | Item | Claimed Status | Actual Status | Category | Evidence |
 |------|---------------|---------------|----------|----------|
 | G8 Horn evaluator truncation removal | CONFIRMED | `evaluator.py` still uses `state.max_iterations` (line 360,565) and `config.k_max` (line 57,514) as hardcoded cutoffs; only external wrapper detects truncation | PARTIAL | evaluator.py:360,565,57,514; g8_evaluator_patch.py |
 | Deli-juris cross-repo interface | CONFIRMED | `juris_calculus_bridge.py` BridgeResult dataclass lacks `derived_bound`, `convergent`, `truncated` fields; backend silently ignores them | UNINTEGRATED | juris_calculus_bridge.py:18-27; juris_calculus_backend.py:_run_claim_bound_verification |
 | Universal grounded SMT | CONFIRMED | `universal_grounded_smt.py` enumerates N=2..13 only; labeled "universal" but bounded | BOUNDED_ONLY | universal_grounded_smt.py |
 | Golden corpus | CONFIRMED | Schema and case_id only in `composition_safety.py`; zero actual four-stage execution results | SPEC_ONLY | composition_safety.py golden corpus section |
 | DAG SCC decomposition | CONFIRMED | `test_scc_correctness_dag` fails, marked KNOWN_LIMITATION, not fixed; previous SCC results not propagated | KNOWN_FAILURE | test_litigation_engineering.py + litigation_engineering.py:check_scc_correctness |
 | Cross-repo integration tests | Implied done | Zero tests connecting Deli↔juris↔Lean | UNINTEGRATED | audit report section 4 |
 | Lean→Python refinement (B4) | Claimed planned | Never started; no certificate verifier, no differential testing | UNINTEGRATED | audit report section 3.3 |
 | B breakthrough (certificate minimization) | CONFIRMED | Z3 exact only for N≤10, greedy otherwise (no approximation guarantee) | BOUNDED_ONLY | breakthrough_verification.py |
 | J breakthrough (cross-jurisdiction) | CONFIRMED | CN→US direction only; no bidirectional or general mapping proof | PARTIAL | breakthrough_verification.py |

 ---

 ## 2. Repair Responsibility

 | Item | Responsible Repo | File(s) to Fix |
 |------|-----------------|----------------|
 | All 13 Lean sorry/evasion | legal-math-modeling | proofs/lean/juris_lean/JurisLean/DungAAF.lean |
 | G8 evaluator truncation | juris-calculus | compiler_core/evaluator.py |
 | Deli bridge new fields | deli-autoresearch | src/deli_autoresearch/juris_calculus_bridge.py, juris_calculus_backend.py, models.py |
 | Cross-repo integration tests | deli-autoresearch | tests/ (new test files) |
 | SMT bounded labeling | juris-calculus | compiler_core/universal_grounded_smt.py |
 | Golden corpus execution | juris-calculus | compiler_core/composition_safety.py + new data dir |
 | DAG SCC bug | juris-calculus | compiler_core/litigation_engineering.py |
 | Lean→Python refinement | legal-math-modeling + juris-calculus | New bridge code + tests |
 | B/J breakthrough rigor | juris-calculus | compiler_core/breakthrough_verification.py |

 ---

 ## 3. Acceptance Conditions

 1. Lean: 0 sorry, 0 axiom, 0 admit; `lake build` 0 errors
 2. iteration_monotone proves actual inclusion `iter k ∅ ⊆ iter (k+1) ∅`, NOT `True`
 3. evaluator.py: zero hardcoded `k_max` or `max_iterations` that can cause silent Horn truncation
 4. Deli bridge: consumes + validates `derived_bound`, `convergent`, `truncated` from juris-calculus
 5. At least 1 automated Lean→Python refinement test exists
 6. cross-repo integration tests count > 0
 7. DAG SCC `KNOWN_LIMITATION` removed, test passes
 8. Golden corpus: 9+ cases in `data/golden_corpus/` with full four-stage artifacts
 9. `universal_grounded_smt.py` explicitly marked as bounded enumeration
 10. B/J breakthroughs: either rigorous proof or downgrade from "mathematical breakthrough" label
 11. UNKNOWN/SKIP/TIMEOUT/BACKEND_UNAVAILABLE never counted as PROVED
 12. No new features added beyond fixing the items above

 ---

 ## 4. LEGACY_PARTIAL_RESULT Markings

 The following findings from previous iterations lack complete proof artifacts and are marked LEGACY_PARTIAL_RESULT:

 - `artifacts/research_manifest.json`: Contains `breakthrough_candidates` scored but not rigorously verified. Marked LEGACY_PARTIAL_RESULT.
 - `benchmarks/sum_of_odds_tail_pass.json`: Placeholder benchmark. Marked LEGACY_PARTIAL_RESULT.
 - All entries in `docs/audit/` referencing completed Lean proofs: Contradicted by current state (0/13). Marked LEGACY_PARTIAL_RESULT.
 - `compiler_core/breakthrough_candidates.py`: Scoring formula valid, but underlying verification claims not rigorous. Marked LEGACY_PARTIAL_RESULT for verification claims only.

 ---

 ## 5. Execution Order

 R0 (this document) → R1 (cross-repo interface) → R2 (G8 Horn truncation) → R3 (G9A Lean theorems) → R4 (Lean→Python refinement) → R5 (remaining gaps)
