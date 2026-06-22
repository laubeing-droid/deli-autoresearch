# Goal
Extend Dung grounded semantics to correctly handle cyclic attack graphs,
producing UNDECIDED (not REJECTED) labels for nodes trapped in cycles.
Target: odd-cycle-free and bidirectional-only cyclic graphs (G9 MVM).

# Target Semantics
Dung (1995) grounded extension with correct three-valued labelling:
- IN (accepted): in the grounded extension
- OUT (rejected): attacked by an IN argument
- UNDECIDED: everything else (cycle members)

# Attack Graph Class
- DAG (acyclic): current implementation works correctly
- Bidirectional (A <-> B): must produce UNDECIDED for both
- Triangle (A -> B -> C -> A): must produce UNDECIDED for all three
- Even cycle (A -> B -> C -> D -> A): must produce UNDECIDED for all
- Mixed: DAG nodes alongside separate cycle components

# Verification Engine
juris-calculus compiler_core.argumentation.grounded_extension
Source: D:\Codex\juris-calculus\源码

# Known Lemmas
- Dung (1995): grounded extension is the least fixed point of the
  characteristic function F(S) = {a | S defends a}
- For DAGs, grounded extension = unique preferred extension
- For odd cycles, grounded extension = empty set (all undecided)
- For bidirectional cycles, grounded extension = empty set

# MVM Breakthrough
Prove that the current grounded_extension() correctly returns
UNDECIDED for cycle members in all non-DAG cases, while preserving
correct DAG behaviour (66,066 existing fixtures must still pass).

The G9 bug fix (commit 113a61e) changed:
  rejected = cids - accepted  -->  rejected = only attacked-by-IN

This should already satisfy the MVM. The auto-research task is to
FORMALLY VERIFY this via regression + counterexample search.
