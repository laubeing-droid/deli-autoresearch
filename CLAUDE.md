# Deli Spec-Driven Control Repository

## Mission

This repository controls two specification-driven programs:

1. JC public baseline audit.
2. Unified Legal Kernel formal proof and runtime refinement.

## Repository Roles

- `deli-autoresearch`: specifications, run state, skills, agents, hooks.
- `legal-math-modeling`: canonical formal semantics and Lean proofs.
- `juris-calculus`: production runtime and certificate producer.

## Mandatory Lifecycle

Every change follows:

REQUIREMENTS
→ DESIGN
→ TASKS
→ EXECUTE ONE TASK
→ VERIFY
→ RED-TEAM
→ COMPLETE / REWORK / BLOCKED

Never implement from an unapproved Draft Spec.

## State Authority

The authoritative state is on disk:

- `specs/<spec>/spec.yaml`
- `specs/<spec>/status.json`
- `specs/<spec>/tasks.md`
- `specs/<spec>/acceptance.md`
- `state/decisions/`
- `state/cross_repo_lock.json`

Do not rely on previous conversation memory.

## Hard Prohibitions

- Do not change licenses.
- Do not change repository visibility.
- Do not rewrite public Git history.
- Do not merge default branches.
- Do not create release tags.
- Do not disclose PATENT_REVIEW content.
- Do not weaken theorem statements.
- Do not add `sorry`, `admit`, custom axioms, `theorem : True`, or constant-true checkers.
- Do not use fixture-only behavior as production proof.
- Do not mix RuleId, ClaimId, and ArgumentId.
- Do not let certificate checkers call the production evaluator.

## Human Decision Required

Stop when a task requires:

- license selection or change;
- patent disclosure;
- ambiguous legal semantics;
- repository visibility change;
- release tagging;
- default-branch merge;
- removal of public history;
- migration of commercial rule assets.

## CI Verification

All formal proofs and runtime tests are verified by GitHub Actions CI.
Claude Code does NOT self-verify proofs. CI is the single source of truth for build/test/pure verification.

## Sorry Allowance

Non-blocking theorems MAY use `sorry` if registered in SORRY_LEDGER.md.
Blocking-path theorems SHALL NOT use `sorry`.

## Commands

- `/spec-status`
- `/spec-requirements <spec-id>`
- `/spec-design <spec-id>`
- `/spec-tasks <spec-id>`
- `/spec-execute <spec-id> <task-id>`
- `/spec-verify <spec-id> <task-id>`
- `/spec-red-team <spec-id> <task-id>`
- `/spec-resume`
- `/spec-report`
