#!/usr/bin/env python3
"""
validate-evidence.py — Check that evidence directories have commands.jsonl.
"""
import os
import sys


def main():
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "specs")
    if not os.path.isdir(specs_dir):
        print("validate-evidence: SKIP — no specs/ directory")
        return 0

    failures = []
    for spec in sorted(os.listdir(specs_dir)):
        spec_path = os.path.join(specs_dir, spec)
        if not os.path.isdir(spec_path):
            continue

        status_file = os.path.join(spec_path, "status.json")
        if not os.path.isfile(status_file):
            continue

        import json
        try:
            with open(status_file) as f:
                status = json.load(f)
        except Exception:
            continue

        # Only check specs that are IN_PROGRESS or later
        if status.get("status") in ("IN_PROGRESS", "VERIFYING", "RED_TEAM", "COMPLETE"):
            commands_file = os.path.join(spec_path, "evidence", "commands.jsonl")
            if not os.path.isfile(commands_file):
                failures.append(f"{spec}: missing evidence/commands.jsonl")

    if failures:
        print(f"validate-evidence: FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print("validate-evidence: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
