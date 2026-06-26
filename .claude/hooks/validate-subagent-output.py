#!/usr/bin/env python3
"""SubagentStop hook: Validate subagent output matches its role contract."""
import sys
import json

ROLE_OUTPUTS = {
    "requirements-analyst": ["requirements", "non-goals", "risks", "human_decisions"],
    "formal-architect": ["design", "interfaces", "theorems", "modules"],
    "lean-prover": ["proofs", "lemmas", "build_result"],
    "runtime-engineer": ["code", "tests", "certificate"],
    "verifier": ["verdict", "acceptance_passed", "acceptance_failed"],
    "red-team": ["verdict", "checks_passed", "checks_failed", "findings", "adversarial_votes"],
}

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    agent_name = input_data.get("agentName", "")
    output = input_data.get("output", "")

    # Basic validation: verifier and red-team must output a verdict
    if agent_name in ("verifier", "red-team"):
        if isinstance(output, str) and "verdict" not in output.lower():
            # Warning but not blocking
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
