# SPEC-250 Design

## Architecture

### Lean Layer (CertificateChecker.lean)

1. **verifyAccept**: checks that all accepted arguments are in AAF args AND in grounded extension
2. **verifyReject**: checks that all rejected arguments are in AAF args AND have an attacker in GE
3. **check**: dispatches on DecisionStatus, enforcing consistency between status and argument lists
4. **evaluate**: maps certificate to (Arg × DecisionStatus) list

### Proof Strategy

- `check_sound`: split on status, use `simp [decide_eq_true_eq]` to decompose Bool.and chains
  - PROVED branch: extract verifyAccept proof, use `verifyAccept_imp_ge` + `decisionProjection` unfolding
  - REFUTED/UNDECIDED branches: extract `accArgs = []` from simp, contradict with `a ∈ accArgs`
  - TAINTED branch: `simp at h` closes immediately
- `certificate_verifies`: same structure as check_sound

### Python Layer

- `certificate_checker.py`: four certificate types (Horn, IN, OUT, UNDEC), each with independent `verify` method
- `test_certificate_checker.py`: positive tests for each certificate type + independence check
- `test_certificate_mutations.py`: mutation tests for 6 tampering scenarios

## Key Design Decision

Using `simp [decide_eq_true_eq]` to decompose `Bool.and` chains with `decide` wrappers. After `simp`, the hypothesis becomes a conjunction of Props (not Bools), enabling direct `rw` on equality proofs. The depth of `.1` projections varies by branch structure:
- REFUTED: `h.1.1` for `accArgs = []`
- UNDECIDED: `h.1.1.1` for `accArgs = []`
