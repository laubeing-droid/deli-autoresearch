#!/usr/bin/env python3
"""
sorry-gate.py — CI gate that checks sorry compliance.

Usage:
    python scripts/sorry-gate.py --ledger SORRY_LEDGER.md --strict-for blocking
    python scripts/sorry-gate.py --ledger SORRY_LEDGER.md

Modes:
    --strict-for blocking: Zero tolerance for sorry in blocking-path theorems.
    Without --strict-for: Check that all sorrys have ledger entries.

Exit codes:
    0 — gate passed
    1 — gate failed
"""
import argparse
import os
import re
import sys
import json
from pathlib import Path

# 18 blocking-path theorems — must be kept in sync with Playbook C §2.2
BLOCKING_THEOREMS = {
    # SPEC-210: Horn Semantics
    "hornClosure_converges",
    "hornStep_monotone",
    "hornClosure_extensive",
    "hornClosure_closed",
    "hornClosure_idempotent",
    # SPEC-230: Argument Compiler
    "compiler_correctness",
    "compileAttacks_exact",
    # SPEC-240: Attack / Grounded Decision
    "attack_compilation_exact",
    "grounded_ext_is_complete",
    "grounded_decision_matches_formal",
    "decisionProjection_grounds",
    "decisionProjection_completeness",
    # SPEC-250: Certificate Checker
    "checker_sound",
    "certificate_verifies",
    # SPEC-270: Safety Theorems
    "safety_preservation",
    "safety_no_violation",
    # SPEC-280: End-to-End
    "end_to_end_soundness",
    "end_to_end_certificate",
}


def load_blocking_theorems():
    """Load the set of blocking-path theorem names."""
    return BLOCKING_THEOREMS


def scan_lean_files(repo_root):
    """Scan all .lean files for sorry occurrences."""
    sorry_pattern = re.compile(r'\bsorry\b')
    results = []
    lean_dirs = [
        os.path.join(repo_root, "proofs", "lean"),
    ]

    for lean_dir in lean_dirs:
        if not os.path.isdir(lean_dir):
            continue
        for root, dirs, files in os.walk(lean_dir):
            for fname in files:
                if not fname.endswith(".lean"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line_no, line in enumerate(f, 1):
                            if sorry_pattern.search(line):
                                # Skip comments
                                stripped = line.strip()
                                if stripped.startswith("--"):
                                    continue
                                results.append({
                                    "file": fpath,
                                    "line": line_no,
                                    "content": stripped,
                                })
                except Exception:
                    pass

    return results


def parse_ledger(ledger_path):
    """Parse SORRY_LEDGER.md and return set of registered theorem names."""
    registered = set()
    if not os.path.isfile(ledger_path):
        return registered

    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            # Lines like: | theorem_name | ... |
            # or: - theorem_name
            line = line.strip()
            if line.startswith("|") and not line.startswith("|--"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and parts[0] and not parts[0].startswith("-"):
                    registered.add(parts[0])
            elif line.startswith("- "):
                name = line[2:].split(":")[0].strip()
                if name:
                    registered.add(name)

    return registered


def main():
    parser = argparse.ArgumentParser(description="Sorry gate for Lean proofs")
    parser.add_argument("--ledger", required=True, help="Path to SORRY_LEDGER.md")
    parser.add_argument("--strict-for", choices=["blocking"], help="Strict mode: zero tolerance for blocking-path theorems")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    args = parser.parse_args()

    repo_root = args.repo_root
    blocking = load_blocking_theorems()
    ledger_registered = parse_ledger(os.path.join(repo_root, args.ledger))

    # Scan lean files for sorry
    sorries = scan_lean_files(repo_root)

    if not sorries:
        print("sorry-gate: PASS — no sorry found")
        return 0

    # For each sorry, determine which theorem it belongs to
    # Simple heuristic: find the nearest preceding theorem/lemma declaration
    failures = []
    warnings = []

    for sorry in sorries:
        # Try to identify the theorem containing this sorry
        thm_name = "unknown"
        try:
            with open(sorry["file"], "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i in range(sorry["line"] - 1, -1, -1):
                line = lines[i].strip()
                m = re.match(r'(?:theorem|lemma|def)\s+(\w+)', line)
                if m:
                    thm_name = m.group(1)
                    break
        except Exception:
            pass

        sorry_info = {
            "theorem": thm_name,
            "file": sorry["file"],
            "line": sorry["line"],
        }

        if args.strict_for == "blocking":
            # In strict mode: any sorry in a blocking theorem = FAIL
            if thm_name in blocking:
                failures.append(sorry_info)
            elif thm_name not in ledger_registered:
                # Non-blocking sorry without ledger entry
                failures.append(sorry_info)
            else:
                warnings.append(sorry_info)
        else:
            # Normal mode: all sorrys must have ledger entries
            if thm_name not in ledger_registered:
                failures.append(sorry_info)
            else:
                warnings.append(sorry_info)

    if failures:
        print(f"sorry-gate: FAIL — {len(failures)} unauthorized sorry(s):")
        for f in failures:
            print(f"  BLOCKED: {f['theorem']} at {f['file']}:{f['line']}")
        return 1

    if warnings:
        print(f"sorry-gate: PASS with {len(warnings)} registered sorry(s):")
        for w in warnings:
            print(f"  OK: {w['theorem']} at {w['file']}:{w['line']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
