# SPEC-010 Acceptance Criteria

## Global

- AC-010-G01: 全部 11 个 Task 按序完成
- AC-010-G02: 每个 Task 的 evidence 文件存在
- AC-010-G03: 控制链路完整（init → requirements → design → tasks → execute → verify → red-team → complete）

## Per-Task

| Task | Acceptance ID | Criteria |
|------|--------------|----------|
| TASK-010-001 | AC-010-001 | pytest exits 0 |
| TASK-010-002 | AC-010-002 | pytest exits non-zero (intentional failure) |
| TASK-010-003 | AC-010-003 | verifier verdict = REWORK |
| TASK-010-004 | AC-010-004 | pytest exits 0 (fixed) |
| TASK-010-005 | AC-010-005 | verifier verdict = PASS_CANDIDATE |
| TASK-010-006 | AC-010-006 | red_team_verdict = PASS or PASS_WITH_LIMITS |
| TASK-010-007 | AC-010-007 | status = IN_PROGRESS with partial state |
| TASK-010-008 | AC-010-008 | resume identifies correct state |
| TASK-010-009 | AC-010-009 | HUMAN_DECISION_REQUIRED set → decision → cleared |
| TASK-010-010 | AC-010-010 | sorry gate: unregistered FAIL, registered PASS, blocking FAIL |
| TASK-010-011 | AC-010-011 | status = COMPLETE |

## Evidence Requirements

每个 Task 必须在 `specs/010-demo/evidence/test-results/` 产生一个输出文件，记录命令和结果。
