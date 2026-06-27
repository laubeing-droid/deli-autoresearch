# SPEC-250 Tasks

## TASK-250-001: Define checker functions in Lean
- Status: DONE
- Files: CertificateChecker.lean (verifyAccept, verifyReject, check, evaluate)

## TASK-250-002: Prove check_sound
- Status: DONE
- Lean proof: split on status, simp + verifyAccept_imp_ge for PROVED, accArgs=[] contradiction for others

## TASK-250-003: Prove certificate_verifies
- Status: DONE
- Lean proof: same structure as check_sound

## TASK-250-004: Create Python certificate checker
- Status: DONE
- Files: compiler_core/certificate_checker.py (pre-existing, verified independent)

## TASK-250-005: Create test_certificate_checker.py
- Status: DONE
- 17 tests: Horn chain, GroundedIN, OUT, UNDEC, independence check

## TASK-250-006: Create test_certificate_mutations.py
- Status: DONE
- 11 tests: removed premise, forged rule, forged attack, forged label, input hash

## TASK-250-007: Red-team + finalize
- Status: DONE
- Evidence: build logs, test logs, axiom audit, independence verification
