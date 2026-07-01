# Publishing Checklist

This document describes local readiness checks before any public publishing step. It does not authorize pushing, tagging, releasing, or changing repository visibility.

## Release Boundary

The public repository should contain only the auditable Deli kernel:

- orchestration runtime;
- source-bounded retrieval and evidence routing;
- schemas and examples;
- deterministic tests and replay fixtures;
- public documentation and audit reports.

Do not publish:

- customer data;
- commercial rule libraries;
- lawyer workflow assets;
- litigation strategy;
- private benchmarks;
- private OCR corpora;
- local bridge runtime state;
- machine-specific paths, tokens, proxy values, or private sync roots.

## Required Local Gates

Run from the repository root.

```powershell
git status --short --branch
python -m compileall -q src scripts spc_analysis
python -m pytest -q
```

Run source-bounded tests when evidence, retrieval, memory, disclosure, or research-profile behavior changed.

```powershell
python -m pytest tests/test_source_registry.py tests/test_retrieval_policy.py tests/test_memory_router.py tests/test_trial_harness.py tests/test_search_frontier.py tests/test_verification_backends.py tests/test_disclosure_gate.py tests/test_local_history_profile.py -q
```

Run disclosure scans for these classes:

- Windows absolute-path syntax;
- user-home paths;
- legacy local roots;
- private workspace roots;
- private sync roots;
- local proxy endpoints;
- common token and private-key formats.

All tracked-file scans should return no matches.

## Dependency And Advisory Checks

Deli currently declares no runtime dependencies. The minimum local supply-chain gate is:

```powershell
python -m pip install -e .
python -m pip check
```

If a vulnerability advisory tool is used, do not claim success unless its remote advisory query completes. A network timeout is a release blocker, not a pass.

## Cross-Repo Inputs

External roots must come from environment variables or sibling-repository discovery:

- `JURIS_CALCULUS_ROOT`
- `LEGAL_MATH_MODELING_ROOT`
- `MINNAN_PROFILE_ROOT`
- `SPC_OCR_JSON_DIR`

If an external formal/runtime engine is missing, the backend must fail closed.

## Metadata

Suggested repository metadata:

- Name: `deli-autoresearch`
- Description: `Source-bounded long-horizon proof research orchestration framework`
- Topics: `mathematical-proofs`, `research-automation`, `agent-orchestration`, `verification`, `python`

## Evidence To Keep

Keep local release evidence under `docs/audit/` or tracked spec evidence only when it is sanitized and reproducible. Runtime output remains ignored under `runtime/`.
