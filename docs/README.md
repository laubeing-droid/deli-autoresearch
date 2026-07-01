# Documentation Index

This directory contains the public support documentation for Deli AutoResearch. Runtime state and private evidence do not belong here.

## Start Here

| Document | Use it for |
| --- | --- |
| `../README.md` | Project overview, install, quick start, runtime model, verification commands |
| `../CONTRIBUTING.md` | Local contribution workflow and review checklist |
| `../PLANS.md` | Current local execution and verification snapshot |
| `publishing.md` | Pre-publication boundary and local audit gates |
| `source_bounded_research.md` | Source registry, retrieval, candidate, finding, and disclosure model |

## Research Model

| Document | Use it for |
| --- | --- |
| `research/methodology.md` | Research loop, verdict semantics, stall/pivot model |
| `research/formal-trust-boundary.md` | Allowed and forbidden formal-trust claims |
| `research/template-authoring-guide.md` | Template interfaces and validator expectations |
| `research/case-study-legal-formalization.md` | Historical application note |
| `research/cross-repo-final-report.md` | Historical cross-repo result summary |
| `research/opportunity-backlog.md` | Candidate future work |

## Operations And Audit

| Document | Use it for |
| --- | --- |
| `claude-code-operations.md` | Spec-driven Claude Code workflow |
| `audit/pre-release-audit-2026-07-01.md` | Latest local pre-release audit evidence |
| `audit/phase-a-trust-baseline.md` | Earlier trust baseline |
| `execution/THEOREM_OBLIGATIONS.md` | Theorem obligation tracking |
| `remediation/` | Historical remediation reports |

## Documentation Rules

- Keep public docs free of machine-specific absolute paths, proxy endpoints, credentials, and private data roots.
- Use placeholders such as `<deli-autoresearch-root>`, `<juris-calculus-root>`, and `<legal-math-modeling-root>`.
- Do not turn historical empirical evidence into a formal-proof claim.
- When counts or commit ids change, update `PLANS.md` or an audit report in the same local commit.
