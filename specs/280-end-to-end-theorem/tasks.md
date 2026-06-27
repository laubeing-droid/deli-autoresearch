# SPEC-280 Tasks

## T1 — Lean End-to-End Module
- [x] Define `evaluate` (model → AAF → decision projection per argument)
- [x] Define `check_model` (wrapper: model → DungAAF → check)
- [x] Prove `check_proved_accepted_in_grounded` (helper)
- [x] Prove `check_proved_accepted_in_args` (helper)
- [x] Prove `certified_end_to_end_refinement` (BLOCKING, 0 sorry)
- [x] Prove `accepted_in_grounded` (corollary)

## T2 — Sorry Closing Pass
- [x] Close SORRY-002 (provenance_sound): strengthen hypothesis
- [x] Close burden_unsatisfied_blocks_defense: prove via push_neg
- [x] Close DDL sorry entries as DEFERRED domain axioms

## T3 — Python End-to-End Tests
- [x] test_end_to_end.py: 13 tests covering composition, checker acceptance, safety, fail-closed, biconditional

## T4 — Lifecycle Files
- [x] spec.yaml, requirements.md, tasks.md, acceptance.md, design.md, status.json
- [x] evidence/red-team-verdict.json
