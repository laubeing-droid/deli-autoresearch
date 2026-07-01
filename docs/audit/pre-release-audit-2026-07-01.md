# Deli Pre-Release Audit - 2026-07-01

## Verdict

- Overall: `BLOCKED_EXTERNAL_VULNERABILITY_DB`
- Local auditable kernel gates: `PASS`
- Release claim allowed: local source, disclosure, semantic, and runtime gates passed.
- Release claim not allowed: external vulnerability database scan passed.

## Baseline

- Repository: `deli-autoresearch`
- Starting HEAD: `a4b21ca5ea635cfd6d2a840ea6963d53f79c35f5`
- Starting branch state: `main...origin/main [ahead 3]`
- Starting dirty tree: clean
- Policy basis: fail-closed, source-bounded evidence, no direct model/web promotion to verified findings.

## L1 Supply Chain

- `pyproject.toml` runtime dependencies: `[]`
- `python -m pip check` in the global interpreter reported unrelated global environment conflicts:
  - `googleapis-common-protos` requires newer `protobuf`
  - `kubernetes` requires newer `pyyaml`
  - `opentelemetry-proto` requires newer `protobuf`
- Isolated temporary venv with `HTTP_PROXY` and `HTTPS_PROXY` set to `<local-proxy-url>`:
  - `pip install --upgrade pip setuptools wheel pip-audit`: passed
  - `pip install -e .`: passed
  - `python -m pip check`: `No broken requirements found.`
  - `python -m pip_audit --local --skip-editable --progress-spinner off --timeout 60`: failed with `ReadTimeout` against `pypi.org`
- Assessment: project dependency surface is empty and isolated install is clean, but external vulnerability DB verification is blocked by network timeout.

## L2 Disclosure And Sanitization

- Credential/private-key scan:
  - Command class: `git grep` for private-key headers, AWS keys, GitHub tokens, OpenAI-style tokens, Slack tokens.
  - Result: no matches.
- Secret assignment scan:
  - Command class: case-insensitive `git grep` for `api_key`, `secret`, `token`, `password` assignments.
  - Result: no matches.
- Local path and proxy disclosure scan:
  - `git grep` for Windows absolute-path syntax: no matches.
  - `git grep` for the user-home path: no matches.
  - `git grep` for the legacy Claude root: no matches.
  - `git grep` for the Codex workspace root: no matches.
  - `git grep` for the private sync root: no matches.
  - `git grep` for the local proxy endpoint: no matches.
- Remediation applied:
  - Replaced hard-coded JC/Minnan/SPC roots with env or sibling-repo resolvers.
  - Sanitized tracked docs, examples, and historical evidence to placeholders.
  - Sanitized historical pytest output paths.

## L3 Semantic Alignment

- `python -m deli_autoresearch.cli --workspace . doctor`: passed and wrote ignored runtime status.
- Source-bounded tests:
  - `python -m pytest tests/test_source_registry.py tests/test_retrieval_policy.py tests/test_memory_router.py tests/test_trial_harness.py tests/test_search_frontier.py tests/test_verification_backends.py tests/test_disclosure_gate.py tests/test_local_history_profile.py -q`
  - Result: `26 passed`.
- Path resolver / external backend regression:
  - `python -m pytest tests/test_p0_acceptance.py::test_p0_14_e2e_banach_matrix_verification tests/test_cross_repo.py::TestCrossRepoIntegration::test_bridge_all_builtin_cases_pass tests/test_legal_proof.py::test_bridge_full_regression -q`
  - Result: `3 passed`.
- Assessment: LLM/web/model-generated material remains candidate-only unless routed through source registry, MemoryRouter, disclosure gate, and verified backend paths.

## L4 Runtime

- `python -m compileall -q src scripts spc_analysis`: passed.
- `python -m pytest -q`: `158 passed in 23.00s`.

## Changed Files

- Path discovery and fail-closed external roots:
  - `src/deli_autoresearch/constants.py`
  - `src/deli_autoresearch/banach_backend.py`
  - `src/deli_autoresearch/smt_backend.py`
  - `src/deli_autoresearch/batch_litigation.py`
  - `src/deli_autoresearch/research_automation.py`
  - `src/deli_autoresearch/local_history_profile.py`
  - `src/deli_autoresearch/lean_manifest.py`
- Scripts:
  - `scripts/_lock_worker.py`
  - `scripts/run_g9_exploration.py`
  - `spc_analysis/analyze_rules.py`
  - `spc_analysis/build_spc_corpus.py`
  - `spc_analysis/extract_rules.py`
  - `spc_analysis/filter_horn.py`
  - `spc_analysis/validate_juris.py`
- Tests:
  - `tests/test_cross_repo.py`
  - `tests/test_legal_proof.py`
  - `tests/test_p0_acceptance.py`
- Sanitized docs/evidence:
  - `AGENTS.md`
  - `docs/audit/phase-a-trust-baseline.md`
  - `docs/execution/THEOREM_OBLIGATIONS.md`
  - `docs/research/formal-trust-boundary.md`
  - `docs/source_bounded_research.md`
  - `examples/legal_proof/g9_cyclic_grounded_extension.md`
  - `specs/010-demo/evidence/test-results/task-010-001.txt`
  - `specs/010-demo/evidence/test-results/task-010-002.txt`
  - `specs/010-demo/evidence/test-results/task-010-004.txt`
  - `specs/200-unified-legal-schema/evidence/P1-G03-audit.md`
  - `specs/200-unified-legal-schema/evidence/P1-G03-status.md`
  - `specs/290-formal-release/evidence/audit-report.md`
  - `specs/290-formal-release/evidence/release-boundary-report.md`
- Project memory:
  - `MEMORY.md`

## Remaining Risk

- `pip-audit` external vulnerability lookup timed out through the configured proxy. Do not claim external vulnerability scan success until that query completes.
- The global Python interpreter has package conflicts unrelated to Deli. Isolated venv install and `pip check` are clean.
- No push, tag, release, or GitHub visibility change was performed.
