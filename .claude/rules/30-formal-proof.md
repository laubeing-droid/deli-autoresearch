---
paths:
  - "../legal-math-modeling/**/*.lean"
  - "specs/2*/**"
---

# Formal Proof Rules

- Reuse sealed formal modules.
- Do not create parallel Horn or Dung semantics.
- Do not weaken target theorem statements.
- Do not introduce `sorry`, `admit`, custom axioms, or `theorem : True` for blocking-path theorems.
- Non-blocking theorems MAY use `sorry` only if registered in SORRY_LEDGER.md.
- Do not pass correctness as an assumption.
- A theorem found false must produce a minimal counterexample and BLOCKED status.
- A test or finite enumeration does not replace a universal Lean proof.
- The theorem name must match its actual strength.
