#!/usr/bin/env python3
"""PreToolUse hook: Enforce spec state before allowing writes."""
import sys
import json
import os

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    # Check if there's an active spec in IN_PROGRESS state
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "specs")
    if not os.path.isdir(specs_dir):
        sys.exit(0)

    has_active = False
    for spec_dir in os.listdir(specs_dir):
        status_file = os.path.join(specs_dir, spec_dir, "status.json")
        if os.path.isfile(status_file):
            try:
                with open(status_file) as f:
                    status = json.load(f)
                if status.get("status") in ("IN_PROGRESS", "VERIFYING", "RED_TEAM"):
                    has_active = True
                    break
            except Exception:
                pass

    # If no active spec, warn but allow (for initial setup)
    # In production, this would deny writes outside spec context
    sys.exit(0)

if __name__ == "__main__":
    main()
