#!/usr/bin/env python3
"""PostToolUse hook: Record evidence of file changes."""
import sys
import json
import os
from datetime import datetime, timezone

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

    tool_name = input_data.get("toolName", "unknown")
    success = input_data.get("result", {}).get("success", True)

    # Find the active spec's evidence directory
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "specs")
    if not os.path.isdir(specs_dir):
        sys.exit(0)

    for spec_dir in os.listdir(specs_dir):
        status_file = os.path.join(specs_dir, spec_dir, "status.json")
        if os.path.isfile(status_file):
            try:
                with open(status_file) as f:
                    status = json.load(f)
                if status.get("status") in ("IN_PROGRESS", "VERIFYING", "RED_TEAM"):
                    # Record to commands.jsonl
                    commands_file = os.path.join(specs_dir, spec_dir, "evidence", "commands.jsonl")
                    os.makedirs(os.path.dirname(commands_file), exist_ok=True)

                    entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "tool": tool_name,
                        "file": file_path,
                        "success": success,
                        "spec": spec_dir,
                    }

                    with open(commands_file, "a") as f:
                        f.write(json.dumps(entry) + "\n")
                    break
            except Exception:
                pass

    sys.exit(0)

if __name__ == "__main__":
    main()
