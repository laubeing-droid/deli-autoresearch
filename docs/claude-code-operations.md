# Claude Code Operations Guide

## Starting a Session

```bash
cd deli-autoresearch
claude
```

Claude Code automatically loads:
- `CLAUDE.md` (root instructions)
- `.claude/rules/` (6 scoped rules)
- `.claude/skills/` (11 lifecycle skills)
- `.claude/agents/` (7 role-separated agents)
- `.claude/hooks/` (7 enforcement hooks via settings.json)

## Skills Reference

### /spec-init `<spec-id>` `<title>`
Create a new spec directory with empty files and DRAFT status.

### /spec-status
Display status of all specs. Shows: spec-id, title, status, task progress.

### /spec-requirements `<spec-id>`
Analyze repositories and produce structured requirements.md with numbered REQ IDs.

### /spec-design `<spec-id>`
Produce design.md with architecture, interfaces, models, error semantics.

### /spec-tasks `<spec-id>`
Compile requirements and design into atomic tasks with dependency DAG.

### /spec-execute `<spec-id>` `<task-id>`
Execute one task in a worktree. Creates worktree, runs implementation agent, pushes to spec branch.

### /spec-verify `<spec-id>` `<task-id>`
Verify task completion: CI green, acceptance checks, file scope, sorry ledger.

### /spec-red-team `<spec-id>` `<task-id>`
Three-layer defense: CI mechanical checks → semantic analysis (RT-001~RT-008) → adversarial verification (3 agents).

### /spec-resume
Resume from disk state. Scans status.json files, finds next actionable task.

### /spec-decide `<spec-id>` `<topic>` `"<text>"`
Record a human decision. Only records, never decides.

### /spec-report
Generate progress report across all specs.

## Hooks Behavior

| Hook | Trigger | Behavior |
|------|---------|----------|
| block-dangerous-command | Bash | Blocks git reset --hard, force push, rm -rf, etc. |
| enforce-file-scope | Write/Edit | Checks file is within allowed paths |
| enforce-spec-state | Write/Edit | Checks spec allows writes |
| protect-theorem-statement | Write/Edit | Blocks sorry/admit in blocking theorems |
| record-evidence | Write/Edit | Logs changes to commands.jsonl |
| validate-subagent-output | SubagentStop | Checks agent output matches role contract |
| validate-stop | Stop | Warns if IN_PROGRESS task abandoned |

Override: Hooks return JSON with `permissionDecision: "deny"` to block.

## CI Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| ci.yml | push/PR | pytest |
| formal-proof.yml | .lean changes | lake build + sorry gate + axiom audit |
| runtime-tests.yml | .py/.yaml changes | JC runtime tests |
| spec-integrity.yml | push/PR | spec completeness + dependency DAG |
| safety-gates.yml | push to main | LICENSE protection + theorem strength |

## Worktree Lifecycle

```bash
# Create worktree for a task
python scripts/worktree-create.py --spec SPEC-210 --task TASK-210-005

# Work in .worktrees/210/210-005/
# Push to spec/210/210-005 branch
# CI runs on push

# Cleanup after merge
python scripts/worktree-cleanup.py --spec SPEC-210

# Cleanup stale worktrees (> 7 days)
python scripts/worktree-cleanup.py --stale 7 --dry-run
python scripts/worktree-cleanup.py --stale 7
```

## Validation Scripts

```bash
python scripts/validate-spec-completeness.py    # Check spec files exist
python scripts/check-dependency-dag.py          # No circular dependencies
python scripts/validate-sorry-ledger.py          # 18 blocking theorems listed
python scripts/validate-evidence.py              # Evidence files present
python scripts/sorry-gate.py --ledger SORRY_LEDGER.md --strict-for blocking
python scripts/theorem-hash-gate.py --expected-dir specs/*/evidence/hashes/
```

## Sorry Gate

Blocking-path theorems (18 total) SHALL NOT use `sorry`.
Non-blocking theorems MAY use `sorry` if registered in `SORRY_LEDGER.md`.

```bash
# Check all sorrys (must have ledger entry)
python scripts/sorry-gate.py --ledger SORRY_LEDGER.md

# Strict mode (zero tolerance for blocking path)
python scripts/sorry-gate.py --ledger SORRY_LEDGER.md --strict-for blocking
```
