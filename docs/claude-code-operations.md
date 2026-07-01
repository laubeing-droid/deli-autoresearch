# Claude Code Operations Guide

This repository includes a spec-driven Claude Code control surface. It is useful for structured local execution, but the repository state on disk remains authoritative.

## Startup

Start from the repository root:

```powershell
claude
```

Claude Code reads:

- `CLAUDE.md`;
- `.claude/rules/`;
- `.claude/skills/`;
- `.claude/agents/`;
- `.claude/hooks/`;
- tracked spec files under `specs/`;
- tracked decisions under `state/decisions/`.

Do not rely on conversation memory as the source of truth.

## Spec Lifecycle

```text
requirements -> design -> tasks -> execute -> verify -> red-team -> complete/rework/blocked
```

Do not implement from an unapproved draft spec.

## Commands

| Command | Purpose |
| --- | --- |
| `/spec-init <spec-id> <title>` | Create a spec directory in draft state |
| `/spec-status` | Read spec status from disk |
| `/spec-requirements <spec-id>` | Draft numbered requirements |
| `/spec-design <spec-id>` | Draft architecture and contracts |
| `/spec-tasks <spec-id>` | Convert requirements/design into atomic tasks |
| `/spec-execute <spec-id> <task-id>` | Execute one scoped task |
| `/spec-verify <spec-id> <task-id>` | Verify scope, CI/test evidence, and acceptance |
| `/spec-red-team <spec-id> <task-id>` | Run adversarial review |
| `/spec-decide <spec-id> <topic> "<text>"` | Record a human decision |
| `/spec-resume` | Resume from disk state |
| `/spec-report` | Generate a spec progress report |

## Hook Intent

Hooks are guardrails, not proof engines.

| Hook | Intent |
| --- | --- |
| `block-dangerous-command` | Block destructive git or filesystem operations |
| `enforce-file-scope` | Keep edits within approved paths |
| `enforce-spec-state` | Prevent writes when the spec state forbids them |
| `protect-theorem-statement` | Block forbidden proof weakening |
| `record-evidence` | Record command evidence |
| `validate-subagent-output` | Check role output shape |
| `validate-stop` | Warn on abandoned in-progress tasks |

## Local Verification

```powershell
python -m pytest -q
python -m compileall -q src scripts spc_analysis
python scripts/validate-spec-completeness.py
python scripts/check-dependency-dag.py
python scripts/validate-evidence.py
```

Formal proof checks belong to the formal repository and CI. Deli may read manifests and backend results, but it must not present agent text as a formal proof.

## Worktrees

Use worktrees only for scoped spec tasks:

```powershell
python scripts/worktree-create.py --spec SPEC-210 --task TASK-210-005
python scripts/worktree-cleanup.py --spec SPEC-210 --dry-run
```

Before deleting any worktree, verify the resolved path stays inside the repository worktree area.

## Stop Conditions

Stop and require a human decision when a task involves:

- license changes;
- repository visibility;
- release tags;
- default-branch merges;
- patent-review material;
- ambiguous legal semantics;
- migration of commercial rule assets;
- changes to checker acceptance or verified-finding semantics.
