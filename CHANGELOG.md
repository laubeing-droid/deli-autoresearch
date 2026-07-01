# Changelog

## Unreleased

- docs: rewrite public support documentation around source-bounded research, fail-closed verification, publishing gates, and current local verification commands.
- audit: add Deli pre-release audit report and keep external vulnerability database timeout as an explicit blocker rather than claiming success.
- hygiene: remove tracked machine-specific absolute paths and private data defaults from source, tests, scripts, docs, examples, and historical evidence.
- runtime: route external repository roots through environment variables or sibling-repository discovery.

## v0.1.1 (2026-06-25)

- hygiene: remove cross-repo scratch files and stray OS residue.
- gitignore: add scratch, artifact, and OS-residue patterns.
- planning: sync cross-repo heads, test baseline, and Phase 4 delivery notes.
- ci: add GitHub Actions workflow.

## v0.1.0

- Initial local implementation of the proof research runtime.
- Claim, evidence, finding, and direction lifecycle support.
- Independent work and verification flow.
- `codex-bridge` backend for multi-session coordination.
- Tail-pass completion policy.
- Task asset loading from `examples/`.
- Replay benchmark support.
