#!/usr/bin/env python3
"""PreToolUse hook: Block dangerous Bash commands."""
import sys
import json

DANGEROUS_PATTERNS = [
    "git reset --hard",
    "git push --force",
    "git push -f",
    "rm -rf /",
    "rm -rf ~",
    "git branch -D",
    "git tag -d",
    "git filter-branch",
    "git rebase -i",
    "git commit --amend",
    "git checkout main",
    "git merge main",
]

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    command = input_data.get("toolInput", {}).get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if pattern in command.lower():
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked dangerous command: {pattern}"
                }
            }
            print(json.dumps(result))
            sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
