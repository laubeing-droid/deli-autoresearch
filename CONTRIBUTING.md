# Contributing to Deli AutoResearch

This project is small, but its invariants are strict. A contribution is acceptable only when it preserves the research control plane, source-bounded evidence model, and fail-closed verification behavior.

## Ground Rules

- Preserve the single-writer runtime model.
- Do not let work or verification agents write task state directly.
- Keep process arbitration in code, not hidden in prompts.
- Keep `derived`, `model_generated`, and open-web material candidate-only unless a source or backend gate promotes it.
- Do not weaken checker acceptance standards, disclosure gates, or verification status semantics.
- Do not commit `runtime/`, private data roots, bridge request/response state, credentials, local proxy values, or machine-specific absolute paths.
- Do not push, tag, release, or change repository visibility as part of a normal local contribution.

## Development Workflow

1. Check the working tree.

```powershell
git status --short --branch
```

2. Read the project rules and memory.

```powershell
Get-Content AGENTS.md
Get-Content MEMORY.md
```

3. Make the smallest coherent change.
4. Add or update tests for lifecycle, evidence, retrieval, backend, or disclosure behavior.
5. Run verification.

```powershell
python -m compileall -q src scripts spc_analysis
python -m pytest -q
```

6. Run disclosure scans before committing.

```powershell
git grep -n -E '[A-Z]:\\' -- .
git grep -n -F '<legacy-local-root-token>' -- .
git grep -n -F '<local-proxy-endpoint>' -- .
```

The scans should not return tracked-file matches.

## Where To Put Changes

| Change type | Preferred location |
| --- | --- |
| Runtime behavior | `src/deli_autoresearch/` |
| Source registry or retrieval policy | `src/deli_autoresearch/source_registry.py`, `src/deli_autoresearch/retrieval_policy.py`, `config/`, `schemas/` |
| Evidence routing | `src/deli_autoresearch/memory_router.py`, `src/deli_autoresearch/disclosure_gate.py` |
| Verification backend contracts | `src/deli_autoresearch/verification_backends.py` and backend-specific modules |
| Templates | `src/deli_autoresearch/templates/`, `docs/research/template-authoring-guide.md` |
| Examples and replay inputs | `examples/`, `benchmarks/` |
| Public docs | `README.md`, `docs/` |
| Spec history and evidence | `specs/` |

## Commit Message Content

Local commits should include:

- files changed;
- root cause;
- new project knowledge;
- impact scope;
- verification commands and results;
- remaining risk.

## Review Checklist

- Full pytest passes.
- Source-bounded subset passes when relevant.
- No tracked private paths or proxy literals remain.
- `doctor` still writes ignored runtime status.
- Missing external formal/runtime engines fail closed.
- No historical evidence was rewritten in a way that changes its conclusion.
