# SPEC-220 Acceptance

## Lean Verification

```
lake build JurisLean.DDLDefinitions
```

Result: **Build completed successfully**

- 3 theorems fully proved (ordered_next_requires_prior_failure, alternative_imposes_no_order, court_selected_not_auto_chosen)
- 4 non-blocking theorems use sorry (registered in SORRY_LEDGER.md)
- 0 blocking-path sorrys

## Python Tests

```
python -m pytest tests/spec/test_ddl_evaluator.py -v
python -m pytest tests/ -q
```

Result: **327 passed, 38 skipped** (9 new SPEC-220 tests, 0 regressions)

SPEC-220 tests (9 fixtures):
- `test_contract_obligation_satisfied` — contract obligation met
- `test_contract_obligation_violated` — contract obligation gap
- `test_license_permission` — permission as positive state
- `test_tort_prohibition_violated` — tort prohibition
- `test_criminal_constitutive` — constitutive norm
- `test_administrative_obligation_gap` — admin missing premises
- `test_defense_with_burden` — defense with required facts
- `test_reparation_alternative` — ALTERNATIVE reparation mode
- `test_modality_isolation_constitutive_no_violation` — constitutive isolation

## Sorry Gate

4 non-blocking sorrys registered in SORRY_LEDGER.md:
- `violation_implies_norm_active` (closing: SPEC-230)
- `permission_no_direct_violation` (closing: SPEC-230)
- `constitutive_no_direct_violation` (closing: SPEC-230)
- `burden_unsatisfied_blocks_defense` (closing: SPEC-230)
