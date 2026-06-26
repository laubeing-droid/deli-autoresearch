# SPEC-000 Tasks

## TASK-000-001: Audit Current deli-autoresearch

Status: COMPLETE
Dependencies: none
Acceptance: AC-000-001 — current-state inventory documented

## TASK-000-002: Create CLAUDE.md

Status: COMPLETE
Dependencies: TASK-000-001
Allowed files: CLAUDE.md
Acceptance: AC-000-002 — CLAUDE.md exists at root, < 200 lines

## TASK-000-003: Create Scoped Rules

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: .claude/rules/*.md
Acceptance: AC-000-003 — 6 rule files present

## TASK-000-004: Create Lifecycle Skills

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: .claude/skills/*/SKILL.md
Acceptance: AC-000-004 — 11 skill directories with SKILL.md

## TASK-000-005: Create Subagents

Status: COMPLETE
Dependencies: TASK-000-003
Allowed files: .claude/agents/*.md
Acceptance: AC-000-005 — 7 agent files present

## TASK-000-006: Create Hooks and settings.json

Status: COMPLETE
Dependencies: TASK-000-003
Allowed files: .claude/hooks/*.py, .claude/settings.json
Acceptance: AC-000-006 — 7 hooks + settings.json

## TASK-000-007: Create State Schemas

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: schemas/spec-run-result.schema.json
Actions:
1. Create JSON Schema for headless spec-run output
2. Define required fields per Playbook A section 14
Acceptance: AC-000-007 — valid JSON Schema draft-07

## TASK-000-008: Create State Validation Scripts

Status: COMPLETE
Dependencies: TASK-000-007
Allowed files: scripts/validate-*.py, scripts/check-*.py
Acceptance: AC-000-008 — 4 validation scripts exit 0

## TASK-000-009: Create Worktree Scripts

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: scripts/worktree-create.py, scripts/worktree-cleanup.py
Actions:
1. Create worktree-create.py for spec worktree branches
2. Create worktree-cleanup.py for removing stale worktrees
Acceptance: AC-000-009 — scripts functional

## TASK-000-010: Create Headless Output Schema

Status: COMPLETE
Dependencies: TASK-000-007
Allowed files: schemas/*.json
Actions:
1. Complete JSON Schema covering all fields from Playbook A section 14
Acceptance: AC-000-010 — valid JSON Schema

## TASK-000-011: Create GitHub Actions CI Workflows

Status: COMPLETE
Dependencies: TASK-000-012, TASK-000-013
Allowed files: .github/workflows/*.yml
Acceptance: AC-000-011 — 4 new workflow files

## TASK-000-012: Create Sorry Gate Script

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: scripts/sorry-gate.py
Acceptance: AC-000-012 — blocks unregistered sorry

## TASK-000-013: Create Theorem Hash Gate Script

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: scripts/theorem-hash-gate.py
Acceptance: AC-000-013 — verifies hash consistency

## TASK-000-014: Create Operator Documentation

Status: COMPLETE
Dependencies: TASK-000-002
Allowed files: docs/claude-code-operations.md
Actions:
1. Document session startup, all 11 skills, hooks, CI, worktrees
Acceptance: AC-000-014 — docs complete

## TASK-000-015: Run Configuration Validation

Status: COMPLETE
Dependencies: all prior tasks
Acceptance: AC-000-015 — all validation scripts pass
