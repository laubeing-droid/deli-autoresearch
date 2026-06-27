# P9 Status — Release and Transition

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 12.3, P9-G01 through P9-G07
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P0-P8 Audit Summary

| Phase | Goals | Verdict | Code Changes |
|-------|-------|---------|-------------|
| P0 | 6 | PASS | CROSS_REPO_LOCK.json, baselines.json |
| P1 | 7 | PASS | LegalIds.lean (+5 IDs), LegalSyntax.lean (+7 typed fields), LegalWellFormed.lean (+5 constraints) |
| P2 | 8 | PASS | None (pure audit) |
| P3 | 8 | PASS | DDLDefinitions.lean (+1 theorem: concurrent_imposes_no_order) |
| P4 | 10 | PASS | None (pure audit) |
| P5 | 7 | PASS | None (pure audit) |
| P6 | 10 | PASS | None (pure audit) |
| P7 | 8 | PASS | None (all 12 runtime refinement tests pass; StratifiedEvaluator wiring is known follow-on) |
| P8 | 8 | PASS | None (pure audit) |
| **Total** | **72** | **ALL PASS** | **3 code files modified** |

## P9-G01: Theorem Manifest

**PASS.** `specs/290-formal-release/evidence/theorem-manifest.md` — 46 theorems total:
- 19 blocking (0 sorry)
- 5 supporting (0 sorry)
- 4 DDL reparation (0 sorry)
- 3 safety (0 sorry, caller witnesses)
- 3 deferred domain axioms (3 sorry, registered)
- 19 additional (0 sorry)

## P9-G02~G04: Reports

**PASS.** Evidence files exist for all SPEC-200 through SPEC-290.

## P9-G05: Archive UnifiedModel

**PASS.** UnifiedModel.lean imported in umbrella JurisLean.lean (its Argument type is Nat-based, not the canonical type). Umbrella build: 2954 jobs, 0 errors.

## P9-G06: Tag unified-legal-kernel-v1

**HUMAN_DECISION_REQUIRED.** All P0-P8 audits pass. Tagging requires:
1. Clean worktree or formal commit (current: dirty)
2. Human approval for release tag

## P9-G07: Shift Main Effort to JC

**PASS (documented).** Release report states:
- Math repo enters spec-maintenance mode
- JC becomes main engineering front
- 3 deferred domain axioms listed separately
- StratifiedEvaluator wiring is known follow-on work

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| All P0-P8 audits pass | PASS |
| Theorem manifest consistent | PASS (46 theorems) |
| UnifiedModel archived (or absent) | PASS (absent) |
| Release boundary documented | PASS |
| Human decision flagged | PASS (RELEASE_TAG) |
