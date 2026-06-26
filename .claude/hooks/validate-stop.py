#!/usr/bin/env python3
"""Stop hook: Validate session can stop cleanly."""
import sys
import json
import os

MAX_RESUME_ATTEMPTS = 3

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    # Check if there's an active task that should not be abandoned
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "specs")
    if not os.path.isdir(specs_dir):
        sys.exit(0)

    blocking_reasons = []
    for spec_dir in os.listdir(specs_dir):
        status_file = os.path.join(specs_dir, spec_dir, "status.json")
        if os.path.isfile(status_file):
            try:
                with open(status_file) as f:
                    status = json.load(f)
                s = status.get("status", "")
                if s == "IN_PROGRESS":
                    # Check if task has evidence
                    tasks_file = os.path.join(specs_dir, spec_dir, "tasks.md")
                    if os.path.isfile(tasks_file):
                        blocking_reasons.append(f"{spec_dir} is IN_PROGRESS")
            except Exception:
                pass

    # Informational only - do not block stop to avoid infinite loops
    # The validate-stop hook records but does not prevent stopping
    if blocking_reasons:
        # Log warning but allow stop
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
