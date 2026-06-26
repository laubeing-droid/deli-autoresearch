#!/usr/bin/env python3
"""
theorem-strength-gate.py — Verify target theorems have not been weakened.
Compares current theorem statements against recorded hashes.
"""
import os
import sys


def main():
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "specs")
    if not os.path.isdir(specs_dir):
        print("theorem-strength-gate: SKIP — no specs/ directory")
        return 0

    # Check if any hash files exist
    hash_files = []
    for spec in os.listdir(specs_dir):
        hashes_dir = os.path.join(specs_dir, spec, "evidence", "hashes")
        if os.path.isdir(hashes_dir):
            for f in os.listdir(hashes_dir):
                if f.endswith(".json"):
                    hash_files.append(os.path.join(hashes_dir, f))

    if not hash_files:
        print("theorem-strength-gate: SKIP — no hash files found")
        return 0

    # Delegate to theorem-hash-gate.py
    import subprocess
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "theorem-hash-gate.py"),
         "--expected-dir", "specs/*/evidence/hashes/"],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
