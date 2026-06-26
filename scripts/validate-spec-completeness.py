#!/usr/bin/env python3
"""
validate-spec-completeness.py — Check that all spec directories have required files.
"""
import os
import sys
import json

REQUIRED_FILES = [
    "spec.yaml",
    "requirements.md",
    "design.md",
    "tasks.md",
    "acceptance.md",
    "decisions.md",
    "risks.md",
    "status.json",
]

REQUIRED_DIRS = [
    "evidence",
    "evidence/commands.jsonl",
]


def main():
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "specs")
    if not os.path.isdir(specs_dir):
        print("validate-spec-completeness: SKIP — no specs/ directory")
        return 0

    failures = []
    for spec in sorted(os.listdir(specs_dir)):
        spec_path = os.path.join(specs_dir, spec)
        if not os.path.isdir(spec_path):
            continue

        # Skip uninitialized specs (empty placeholder directories)
        has_any = any(os.path.isfile(os.path.join(spec_path, f)) for f in REQUIRED_FILES)
        if not has_any:
            continue

        for req_file in REQUIRED_FILES:
            fpath = os.path.join(spec_path, req_file)
            if not os.path.isfile(fpath):
                failures.append(f"{spec}: missing {req_file}")

        # Check status.json is valid JSON
        status_file = os.path.join(spec_path, "status.json")
        if os.path.isfile(status_file):
            try:
                with open(status_file) as f:
                    json.load(f)
            except Exception as e:
                failures.append(f"{spec}: invalid status.json: {e}")

    if failures:
        print(f"validate-spec-completeness: FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print("validate-spec-completeness: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
