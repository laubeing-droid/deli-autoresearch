#!/usr/bin/env python3
"""PreToolUse hook: Protect theorem statements from unauthorized modification."""
import sys
import json
import os

LEAN_THEOREM_KEYWORDS = [
    "theorem ",
    "lemma ",
    "def ",
    "instance ",
]

BLOCKING_THEOREMS = [
    "hornClosure_converges",
    "grounded_ext_is_complete",
    "compiler_correctness",
    "attack_compilation_exact",
    "grounded_decision_matches_formal",
    "checker_sound",
    "safety_preservation",
    "end_to_end_soundness",
    "hornStep_monotone",
    "hornClosure_extensive",
    "hornClosure_closed",
    "hornClosure_idempotent",
    "compileAttacks_exact",
    "decisionProjection_grounds",
    "decisionProjection_completeness",
    "certificate_verifies",
    "safety_no_violation",
    "end_to_end_certificate",
]

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    file_path = input_data.get("toolInput", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    if not file_path.endswith(".lean"):
        sys.exit(0)

    # Check if the edit targets a blocking theorem name
    old_string = input_data.get("toolInput", {}).get("old_string", "")
    new_string = input_data.get("toolInput", {}).get("new_string", "")

    for thm in BLOCKING_THEOREMS:
        if thm in old_string and old_string != new_string:
            # Check if this is weakening the statement
            # A simple heuristic: if "sorry" or "admit" appears in new_string
            if "sorry" in new_string or "admit" in new_string or "trivial" in new_string:
                result = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked modification of blocking theorem '{thm}': introducing sorry/admit/trivial"
                    }
                }
                print(json.dumps(result))
                sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
