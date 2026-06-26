#!/usr/bin/env python3
"""
theorem-hash-gate.py — CI gate that verifies target theorem hashes have not changed.

Usage:
    python scripts/theorem-hash-gate.py --expected-dir specs/*/evidence/hashes/
    python scripts/theorem-hash-gate.py --expected-dir specs/210-horn-semantics/evidence/hashes/

Reads expected SHA-256 hashes from JSON files in the expected-dir, then recomputes
the hash of each referenced theorem statement and compares.

Exit codes:
    0 — all hashes match
    1 — hash mismatch (theorem weakened or changed)
"""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path


def extract_theorem_statement(lean_file, theorem_name):
    """Extract the statement (type signature) of a named theorem from a .lean file."""
    if not os.path.isfile(lean_file):
        return None

    with open(lean_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Match theorem/lemma definition
    pattern = re.compile(
        rf'(?:theorem|lemma)\s+{re.escape(theorem_name)}\s*(?:\{{[^}}]*\}}\s*)*(?:\([^)]*\)\s*)*:\s*(.+?)(?=\n(?:(?:theorem|lemma|def|where|:=))|\Z)',
        re.DOTALL
    )
    m = pattern.search(content)
    if m:
        return m.group(0).strip()
    return None


def compute_hash(statement):
    """Compute SHA-256 of a theorem statement."""
    if statement is None:
        return None
    return hashlib.sha256(statement.encode("utf-8")).hexdigest()


def load_expected_hashes(hashes_dir):
    """Load expected hashes from evidence/hashes/ directory."""
    expected = {}
    if not os.path.isdir(hashes_dir):
        return expected

    for fname in os.listdir(hashes_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(hashes_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for thm_name, info in data.items():
                    if isinstance(info, dict) and "hash" in info:
                        expected[thm_name] = info
                    elif isinstance(info, str):
                        expected[thm_name] = {"hash": info, "file": fname}
        except Exception:
            pass

    return expected


def main():
    parser = argparse.ArgumentParser(description="Theorem hash gate")
    parser.add_argument("--expected-dir", required=True, help="Glob pattern for hash directories")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = args.repo_root

    # Resolve glob pattern
    import glob
    hash_dirs = glob.glob(os.path.join(repo_root, args.expected_dir))

    if not hash_dirs:
        print("theorem-hash-gate: SKIP — no hash directories found")
        return 0

    failures = []
    checked = 0

    for hash_dir in hash_dirs:
        expected = load_expected_hashes(hash_dir)
        for thm_name, info in expected.items():
            lean_file = os.path.join(repo_root, info.get("file", ""))
            expected_hash = info.get("hash", "")

            statement = extract_theorem_statement(lean_file, thm_name)
            actual_hash = compute_hash(statement)

            checked += 1
            if actual_hash is None:
                failures.append({
                    "theorem": thm_name,
                    "reason": "theorem not found in source",
                    "expected_hash": expected_hash,
                })
            elif actual_hash != expected_hash:
                failures.append({
                    "theorem": thm_name,
                    "reason": "hash mismatch — theorem may have been weakened",
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                })

    if failures:
        print(f"theorem-hash-gate: FAIL — {len(failures)} hash mismatch(es):")
        for f in failures:
            print(f"  {f['theorem']}: {f['reason']}")
        return 1

    print(f"theorem-hash-gate: PASS — {checked} theorem hash(es) verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
