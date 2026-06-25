# PLANS.md -- Execution State

## Current

```
status: IN_PROGRESS
last_verified_commit: 0998897
phase: Phase 4 - 功能扩展深化
```

## Track Status

### Track A: Formal Core Release (COMPLETE)
- legal-math-modeling formal-core release closed (cde13f0)
- GitHub Actions clean build passed
- AxiomAudit independent build passed
- Scan guards: 0 sorry, 0 admit, 0 custom axiom, 0 theorem : True
- Theorem manifest: 39 core + 43 extended + 32 supporting = 75 total

### Track B: Banach (DEFERRED)
- Separate worktree: D:\Claude\数学证明\legal-math-banach
- Route audit complete (subagent Mencius): scaling isomorphism path confirmed
- Mathlib ContractingWith API: fixedPoint, fixedPoint_unique, tendsto_iterate_fixedPoint, apriori/aposteriori error bounds
- Shortest proof path: 4 stages (WeightedMetricSpace -> ContractionCondition -> WeightedBanachFixedPoint -> BanachCertificate)
- 2 new theorems needed: weighted metric completeness via Lipschitz equivalence, Lw <= qw -> ContractingWith q T
- Banach theorem itself not re-proven; Mathlib instances are used
- Not blocking mainline### Track C: Data Protocols (DEFERRED)
- 38-constant calibration, DP adjacency, robust regression protocols
- Schema defined; real data acquisition pending

### Phase 4: Functionality Deepening (DELIVERED)
- Priority: litigation capability > litigation automation > research automation
- P1 delivered:
  - incremental grounded correctness fixes (source SCC bug + external-attacker safety gate)
  - minimal defense witness / shortest defense chain (greedy set cover + Z3 verify)
  - defense_paths, proof_depth, minimal_witnesses on LabelCertificate
  - cross-repo litigation certificate bridge (jc -> Deli)
- Test baseline: jc 227 passed, Deli 77 passed (18 cross-repo)
- Next P1 targets:
  - minimal support / rebuttal sets
  - rule change impact analysis
  - missing evidence checklist
- P2 (litigation automation):
  - legal_proof template batch litigation tasks
  - jc certificate / proof trace / SCC witness auto-feedback to Deli
- P3 (research automation):
  - breakthrough scoring automation
  - multi-task registry scheduling

## Cross-Repo Verification Gates

| Gate | Status | Evidence |
|------|--------|----------|
| legal-math-modeling clean build | PASS | GitHub Actions run + local lake build |
| legal-math-modeling axiom audit | PASS | lake build +JurisLean.AxiomAudit |
| Deli cross-repo tests | PASS | 22 passed in test_cross_repo.py |
| jc full tests | PASS | 241 passed, 38 skipped |
| incremental grounded equivalence | PASS | 6 tests with full-recompute cross-check |
| litigation certificate minimal witness | PASS | cross-repo bridge verified |

## Next-Stage Feature Expansion Entry

Phase 4 is active. The entry point is:
1. P1 litigation capabilities are COMPLETE; all five applied to cross-repo bridge
2. P2 litigation automation depends on completing P1 surface
3. P3 research automation depends on P1 + P2 stability

P1 surface is COMPLETE. Expansion now shifts to P2 template orchestration within Deli.
Banach remains a separate independent track, not blocking functionality deepening.

- P2 (诉讼自动化): COMPLETE — batch litigation runner integrated with legal_proof template
- P3 (研究自动化): COMPLETE — breakthrough scoring, benchmark replay, capability map
