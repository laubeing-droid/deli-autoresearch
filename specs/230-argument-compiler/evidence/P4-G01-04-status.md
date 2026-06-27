# P4-G01~G04 Status — Argument Compiler (Lean)

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 7.3, P4-G01 through P4-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P4-G01: Derivation-backed Argument

**PASS.** `ArgumentCompiler.lean` defines:
- `ValidArgument` (line 16): checks `a.rule ∈ M.rules` AND `∀ sf ∈ a.support_facts, sf ∈ closure`
- `DerivationWitness` (line 22): inductive type with `initial` and `rule` constructors
- `Represents` (line 29): links Argument to DerivationWitness

Argument carries `rule` (RuleId), `support_facts` (List FactId), `sources` (List SourceId) — not uniquified solely by conclusion.

## P4-G02: Canonical Argument Compiler

**PASS.** `compileArguments` (line 37): input = `LegalModel` + `Finset FactId` (closure), output = `List Argument`. One argument per rule whose premises are all in closure. Types are fixed by LegalSyntax.lean.

## P4-G03: Argument Compiler Soundness

**PASS.** `compileArguments_sound` (line 50): fully proven, 0 sorry. Every compiled argument satisfies `ValidArgument M closure a`.

## P4-G04: Argument Compiler Completeness

**PASS.** `compileArguments_complete` (line 63): fully proven, 0 sorry. If rule ∈ M.rules and all premises ∈ closure, then argument exists in compilation output.

---

## Build Verification

```
$ lake build JurisLean.ArgumentCompiler
Build completed successfully (2945 jobs)
```

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Argument carries derivation backing | PASS |
| Compiler input/output types fixed | PASS |
| compileArguments_sound proven (0 sorry) | PASS |
| compileArguments_complete proven (0 sorry) | PASS |
