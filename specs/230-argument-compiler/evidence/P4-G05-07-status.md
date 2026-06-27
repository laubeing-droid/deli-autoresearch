# P4-G05~G07 Status — Attack Compiler (Lean)

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 7.3, P4-G05 through P4-G07
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P4-G05: Typed Attack/Defeat

**PASS.** `AttackDecision.lean` defines:
- `argSet` (line 14): `List Argument → Finset Arg` (Arg = String via `.id.val`)
- `toEdge` (line 17): `Attack → Arg × Arg` (attacker, target via typed IDs)
- `compileAttacks` (line 19): builds `DungAAF` from arguments + attacks

Attack uses typed `ArgumentId` → `Arg` conversion via `.val`. DungAAF uses polymorphic `Arg = String`.

## P4-G06: Attack Soundness

**PASS.** `compileAttacks_sound` (line 26): fully proven, 0 sorry. If edge ∈ compiled attacks, then edge ∈ original attack set AND both endpoints ∈ argSet.

## P4-G07: Attack Completeness

**PASS.** `compileAttacks_complete` (line 34): fully proven, 0 sorry. If edge ∈ attack set and both endpoints ∈ argSet, then edge ∈ compiled attacks.

`compileAttacks_exact` (line 41): biconditional, also proven.

---

## Build Verification

```
$ lake build JurisLean.AttackDecision
Build completed successfully (2948 jobs)
```

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Attack uses typed IDs | PASS |
| compileAttacks_sound proven (0 sorry) | PASS |
| compileAttacks_complete proven (0 sorry) | PASS |
| compileAttacks_exact proven (biconditional) | PASS |
