# Forbidden Claims — Unified Legal Kernel v1

Generated: 2026-06-27

## Claims NOT Supported by Formal Proofs

1. **"The system handles infinite argument sets."** — Proofs use Finset (finite sets).
2. **"Negative premises in Horn rules are supported."** — Only positive Horn rules.
3. **"Preferred or stable semantics are proven."** — Only grounded semantics.
4. **"Cross-jurisdiction mapping is formally verified."** — DEFERRED domain axiom.
5. **"Rule→Norm correspondence is proven."** — DEFERRED (violation_implies_norm_active).
6. **"Permission norms cannot be violated."** — DEFERRED (permission_no_direct_violation).
7. **"The system handles real-time temporal reasoning."** — TimeInterval is Nat-based, not continuous.
8. **"The Banach fixed-point theorem is applied to the legal model."** — Banach track is non-blocking, separate from the main proof chain.
9. **"The certificate checker validates provenance source content."** — Checker validates structure, not content.
10. **"The runtime guarantees termination for all inputs."** — Termination proven for finite well-formed models only.
