#!/usr/bin/env python3
"""
validate-sorry-ledger.py — Validate SORRY_LEDGER.md format and consistency.
"""
import os
import sys
import re


BLOCKING_THEOREMS = {
    "hornClosure_converges", "hornStep_monotone", "hornClosure_extensive",
    "hornClosure_closed", "hornClosure_idempotent",
    "compiler_correctness", "compileAttacks_exact",
    "attack_compilation_exact", "grounded_ext_is_complete",
    "grounded_decision_matches_formal", "decisionProjection_grounds",
    "decisionProjection_completeness",
    "checker_sound", "certificate_verifies",
    "safety_preservation", "safety_no_violation",
    "end_to_end_soundness", "end_to_end_certificate",
}


def main():
    ledger_path = os.path.join(os.path.dirname(__file__), "..", "SORRY_LEDGER.md")
    if not os.path.isfile(ledger_path):
        print("validate-sorry-ledger: SKIP — no SORRY_LEDGER.md")
        return 0

    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that all 18 blocking theorems are listed
    missing = []
    for thm in BLOCKING_THEOREMS:
        if thm not in content:
            missing.append(thm)

    if missing:
        print(f"validate-sorry-ledger: FAIL — {len(missing)} blocking theorem(s) missing from ledger:")
        for m in missing:
            print(f"  {m}")
        return 1

    # Check no blocking theorem appears in the non-blocking entries section
    # Find the "Non-Blocking Sorry Entries" section
    lines = content.split("\n")
    in_nonblocking = False
    violations = []
    for line in lines:
        if "Non-Blocking" in line:
            in_nonblocking = True
            continue
        if in_nonblocking and line.startswith("|"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and parts[0] in BLOCKING_THEOREMS:
                violations.append(parts[0])

    if violations:
        print(f"validate-sorry-ledger: FAIL — blocking theorem(s) in non-blocking section:")
        for v in violations:
            print(f"  {v}")
        return 1

    print("validate-sorry-ledger: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
