# P0-G04 Status — Reproduce Production Attack Compiler Failure

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Confirm whether the production attack graph closes through the canonical contract, or only through the shadow/spec path.

## Products

| Product | Path | Status |
|---------|------|--------|
| Production attack failure report | `specs/230-argument-compiler/evidence/production-attack-repro.md` | CREATED |
| This status report | `specs/230-argument-compiler/evidence/P0-G04-status.md` | CREATED |

**Note**: Playbook E references `specs/230-argument-compiler/evidence/production-attack-gap.md`. File was named `production-attack-repro.md` per user request. Same content.

---

## Verdict

**Production path is broken.** Failure reproduced. Canonical contract is disconnected.

---

## Reproduction Evidence

### Failure 1: Signature Mismatch (Critical)

```
stratified_evaluator.py:67 calls build_attack_graph_from_evaluator(5 args)
argumentation.py:356 defines build_attack_graph_from_evaluator(2 params)
→ TypeError: takes 2 positional arguments but 5 were given
```

**3 of 4 StratifiedEvaluator tests fail**:
```
FAILED test_returns_list_not_irdstate
FAILED test_returns_claims_when_facts_match
FAILED test_accepted_claims_have_epistemic_status
PASSED  test_returns_empty_when_no_facts  (early return, never hits Stage 2)
```

### Failure 2: Field Name Mismatch (High)

```
types.py:97 defines:   exception_chain: List[str]
argumentation.py:383 reads:  getattr(rule, "exception_to", [])
```

Exception-based attack edges are silently missed.

### Failure 3: Canonical Adapter Disconnection (Medium)

`canonical_adapter.py` is never imported by `evaluator.py`, `stratified_evaluator.py`, or `argumentation.py`. The production pipeline bypasses the canonical contract entirely.

---

## Impact Scope

| Affected | Not Affected |
|----------|-------------|
| `StratifiedEvaluator.evaluate()` | Lean proofs (independent) |
| Production 4-stage pipeline | Spec tests (`tests/spec/`) |
| Exception-based attack edges | `evaluate_horn()` (Stage 1) |
| Production → canonical bridge | `grounded_extension()` (Stage 3) |

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Production attack compiler failure reproduced | PASS |
| Failure documented with minimal reproduction | PASS |
| Root cause identified | PASS (3 issues) |
| No P0-G05 work started | PASS |

---

## Downstream Tracking

| Gap | Fix Location | Status |
|-----|-------------|--------|
| Signature mismatch | P4-G08 (Repair JC production attack compiler) | Not started |
| exception_to vs exception_chain | P4-G08 | Not started |
| Canonical adapter disconnection | P7-G01/P7-G02 (Rebuild pipeline + connect adapters) | Not started |
| Spec test vs production divergence | P7-G06 (Differential tests) | Not started |

---

## Allowed Modifications

| File | Operation |
|------|-----------|
| `deli-autoresearch/specs/230-argument-compiler/evidence/production-attack-repro.md` | New |
| `deli-autoresearch/specs/230-argument-compiler/evidence/P0-G04-status.md` | New |

No code files modified. No P0-G05 work started.
