# P6 Status — Certificate & Independent Checker

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 9.3, P6-G01 through P6-G09
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P6-G01: Certificate Schema

**PASS.** LegalSyntax.lean defines Certificate with decision (Decision), provenance (List (ArgumentId × List SourceId)), temporal_record, jurisdiction_record. canonical_schema.py mirrors as Pydantic model.

## P6-G02~G05: Checker Components

**PASS.** CertificateChecker.lean defines:
- `verifyAccept`: all accepted args ∈ aaf.args ∧ ∈ grounded extension
- `verifyReject`: all rejected args have attacker in grounded extension
- `check`: matches on DecisionStatus — PROVED requires non-empty accArgs + verifyAccept; REFUTED requires empty accArgs + non-empty rejArgs + verifyReject; UNDECIDED requires empty both + both verify; TAINTED always false
- `evaluate`: maps accepted args → PROVED, rejected → REFUTED

## P6-G06: Checker Soundness

**PASS.** `check_sound` (line 89): fully proven, 0 sorry. `check=true → ∀ a ∈ accArgs, decisionProjection = PROVED`.

## P6-G07: End-to-End Checker Soundness

**PASS.** `certificate_verifies` (line 110): fully proven, 0 sorry. `check=true → ∀ a ∈ accArgs, a ∈ args ∧ a ∈ grounded`.

## P6-G08: JC Certificate Producer

**PASS.** `EndToEnd.evaluate()` produces `List (Argument × DecisionStatus)`. `check_model()` wraps `CertificateChecker.check`.

## P6-G09: Certificate Mutation Suite

**PASS.** `test_certificate_mutations.py`: 11/11 pass. Corrupts: accepted_args (wrong ids, empty), status (PROVED→REFUTED), decision fields. Checker fails closed on all mutations.

---

## Verification

```
$ lake build JurisLean.CertificateChecker → 2949 jobs, 0 sorry
$ python -m pytest tests/spec/test_certificate_checker.py tests/spec/test_certificate_mutations.py -v
28 passed
```
