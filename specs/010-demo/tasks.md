# SPEC-010 Tasks

## TASK-010-001: Create Demo Function and Tests

```markdown
## TASK-010-001

Status: TODO

Dependencies: none

Allowed files:
- demo/classifier.py
- tests/demo/test_classifier.py
- tests/demo/__init__.py

Actions:
1. Create demo/ directory
2. Create demo/__init__.py
3. Create demo/classifier.py with correct classify_score implementation
4. Create tests/demo/ directory
5. Create tests/demo/__init__.py
6. Create tests/demo/test_classifier.py with all 9 test cases from design
7. Run tests to confirm all pass

Acceptance:
- AC-010-001: `python -m pytest tests/demo/test_classifier.py -v` exits 0

Evidence:
- specs/010-demo/evidence/test-results/task-010-001.txt
```

## TASK-010-002: Implement Intentionally Failing Version

```markdown
## TASK-010-002

Status: TODO

Dependencies: TASK-010-001

Allowed files:
- demo/classifier.py

Actions:
1. Modify classify_score to use incorrect boundary (60 instead of 70)
2. Run tests — expect test_boundary_70 to FAIL

Acceptance:
- AC-010-002: `python -m pytest tests/demo/test_classifier.py -v` exits non-zero

Evidence:
- specs/010-demo/evidence/test-results/task-010-002.txt
```

## TASK-010-003: Verify Rejection

```markdown
## TASK-010-003

Status: TODO

Dependencies: TASK-010-002

Allowed files:
- specs/010-demo/evidence/

Actions:
1. Run verifier agent
2. Confirm verifier outputs REWORK

Acceptance:
- AC-010-003: verifier verdict = REWORK

Evidence:
- specs/010-demo/evidence/test-results/task-010-003.txt
```

## TASK-010-004: Rework Implementation

```markdown
## TASK-010-004

Status: TODO

Dependencies: TASK-010-003

Allowed files:
- demo/classifier.py

Actions:
1. Fix classify_score to use correct boundary (70)
2. Run tests to confirm all pass

Acceptance:
- AC-010-004: `python -m pytest tests/demo/test_classifier.py -v` exits 0

Evidence:
- specs/010-demo/evidence/test-results/task-010-004.txt
```

## TASK-010-005: Verify Pass

```markdown
## TASK-010-005

Status: TODO

Dependencies: TASK-010-004

Allowed files:
- specs/010-demo/evidence/

Actions:
1. Run verifier agent
2. Confirm verifier outputs PASS_CANDIDATE

Acceptance:
- AC-010-005: verifier verdict = PASS_CANDIDATE

Evidence:
- specs/010-demo/evidence/test-results/task-010-005.txt
```

## TASK-010-006: Run Red Team

```markdown
## TASK-010-006

Status: TODO

Dependencies: TASK-010-005

Allowed files:
- specs/010-demo/evidence/

Actions:
1. Run red-team agent (layer 2 semantic checks)
2. Record RT-001 through RT-008 results
3. Record adversarial agent votes (layer 3)
4. Output structured JSON verdict

Acceptance:
- AC-010-006: red_team_verdict = PASS or PASS_WITH_LIMITS

Evidence:
- specs/010-demo/evidence/reports/red-team-verdict.json
```

## TASK-010-007: Interrupt Process

```markdown
## TASK-010-007

Status: TODO

Dependencies: TASK-010-006

Allowed files:
- specs/010-demo/status.json

Actions:
1. Set spec status to IN_PROGRESS (simulating mid-task interrupt)
2. Record partial task state
3. Verify stop hook runs cleanly

Acceptance:
- AC-010-007: status.json shows IN_PROGRESS with partial state recorded

Evidence:
- specs/010-demo/evidence/test-results/task-010-007.txt
```

## TASK-010-008: Resume from Disk State

```markdown
## TASK-010-008

Status: TODO

Dependencies: TASK-010-007

Allowed files:
- specs/010-demo/status.json
- specs/010-demo/tasks.md

Actions:
1. Run spec-resume (reads state from disk, no conversation memory)
2. Verify it identifies the correct next task
3. Verify it resumes from the correct lifecycle phase

Acceptance:
- AC-010-008: resume correctly identifies IN_PROGRESS state and next task

Evidence:
- specs/010-demo/evidence/test-results/task-010-008.txt
```

## TASK-010-009: Test Human Decision State

```markdown
## TASK-010-009

Status: TODO

Dependencies: TASK-010-008

Allowed files:
- specs/010-demo/status.json
- specs/010-demo/decisions.md

Actions:
1. Set spec status to HUMAN_DECISION_REQUIRED
2. Record a mock decision topic in decisions.md
3. Verify spec-decide command records human decision
4. Verify status clears after decision recorded

Acceptance:
- AC-010-009: HUMAN_DECISION_REQUIRED set, decision recorded, status cleared

Evidence:
- specs/010-demo/evidence/test-results/task-010-009.txt
```

## TASK-010-010: Test Sorry Gate

```markdown
## TASK-010-010

Status: TODO

Dependencies: TASK-010-009

Allowed files:
- specs/010-demo/evidence/

Actions:
1. Create a test .lean file with an unregistered sorry
2. Run sorry-gate.py — verify it fails
3. Register the sorry in SORRY_LEDGER.md
4. Run sorry-gate.py — verify it passes
5. Create a test .lean file with a blocking-path sorry
6. Run sorry-gate.py --strict-for blocking — verify it fails regardless of ledger

Acceptance:
- AC-010-010: all 3 sorry gate checks behave correctly

Evidence:
- specs/010-demo/evidence/test-results/task-010-010.txt
```

## TASK-010-011: Close Demo Spec

```markdown
## TASK-010-011

Status: TODO

Dependencies: TASK-010-010

Allowed files:
- specs/010-demo/status.json
- specs/010-demo/spec.yaml

Actions:
1. Run final spec-verify
2. Run final spec-red-team
3. Set status to COMPLETE
4. Update spec.yaml status

Acceptance:
- AC-010-011: status.json and spec.yaml both show COMPLETE

Evidence:
- specs/010-demo/evidence/test-results/task-010-011.txt
```
