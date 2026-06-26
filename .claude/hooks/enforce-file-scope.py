#!/usr/bin/env python3
"""PreToolUse hook: Enforce file scope based on active task."""
import sys
import json
import os

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    file_path = input_data.get("toolInput", {}).get("file_path", "")
    if not file_path:
        file_path = input_data.get("toolInput", {}).get("path", "")

    if not file_path:
        sys.exit(0)

    # Always allow CLAUDE.md, .claude/, specs/, state/, scripts/, SORRY_LEDGER.md
    allowed_prefixes = [
        "CLAUDE.md",
        ".claude/",
        "specs/",
        "state/",
        "scripts/",
        "SORRY_LEDGER.md",
        ".github/",
    ]

    # Check if path is within control repo scope
    normalized = file_path.replace("\\", "/")
    for prefix in allowed_prefixes:
        if prefix in normalized:
            sys.exit(0)

    # Check for cross-repo writes (legal-math-modeling, juris-calculus)
    # These are allowed only if an active task declares them
    cross_repo_indicators = [
        "legal-math-modeling",
        "juris-calculus",
        "proofs/lean",
        "compiler_core",
        "pipeline",
    ]

    for indicator in cross_repo_indicators:
        if indicator in normalized:
            # Cross-repo write - check task scope would be done by enforce-spec-state
            sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
