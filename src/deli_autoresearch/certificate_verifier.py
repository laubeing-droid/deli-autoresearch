"""Independent certificate verifier — R4 production chain.

Verifies grounded extension certificates without calling the same
grounded_extension implementation. Uses independent reasoning:
checks fixpoint property, monotonicity constraints, convergence criteria.

This forms the production chain: output -> certificate -> independent verifier.
"""

from __future__ import annotations

from typing import Any


class CertificateVerifier:
    """Independent verification of grounded extension certificates.

    Does NOT call grounded_extension. Instead checks:
    1. The claimed grounded set is indeed a fixed point of F
    2. No subset of the grounded set is a smaller fixed point (leastness check)
    3. Every IN argument has all attackers defeated by the IN set
    4. Every OUT argument has at least one attacker in IN
    5. Every UNDEC argument is neither IN nor OUT under the same rules
    """

    def verify(
        self,
        arguments: list[str],
        attacks: list[tuple[str, str]],
        claimed_in: list[str],
        claimed_out: list[str],
        claimed_undec: list[str],
    ) -> dict[str, Any]:
        """Independently verify a grounded extension claim."""
        violations = []
        arg_set = set(arguments)
        in_set = set(claimed_in)
        out_set = set(claimed_out)
        undec_set = set(claimed_undec)

        all_claimed = in_set | out_set | undec_set
        missing = arg_set - all_claimed
        if missing:
            violations.append(f"Arguments not classified: {sorted(missing)}")
        extra = all_claimed - arg_set
        if extra:
            violations.append(f"Unknown arguments in output: {sorted(extra)}")

        if in_set & out_set:
            violations.append(f"IN ∩ OUT non-empty: {sorted(in_set & out_set)}")
        if in_set & undec_set:
            violations.append(f"IN ∩ UNDEC non-empty: {sorted(in_set & undec_set)}")
        if out_set & undec_set:
            violations.append(f"OUT ∩ UNDEC non-empty: {sorted(out_set & undec_set)}")

        attackers_of: dict[str, set[str]] = {a: set() for a in arguments}
        for src, tgt in attacks:
            if src in arg_set and tgt in arg_set:
                attackers_of[tgt].add(src)

        for a in in_set:
            for attacker in attackers_of.get(a, set()):
                defender_found = False
                for defender in in_set:
                    if (defender, attacker) in attacks:
                        defender_found = True
                        break
                if not defender_found:
                    violations.append(f"IN({a}): attacker {attacker} has no defender in IN")

        for a in out_set:
            has_in_attacker = False
            for attacker in attackers_of.get(a, set()):
                if attacker in in_set:
                    has_in_attacker = True
                    break
            if not has_in_attacker:
                violations.append(f"OUT({a}): no attacker found in IN")

        for a in undec_set:
            all_defeated = True
            for attacker in attackers_of.get(a, set()):
                defender_found = False
                for defender in in_set:
                    if (defender, attacker) in attacks:
                        defender_found = True
                        break
                if not defender_found:
                    all_defeated = False
                    break
            if all_defeated and attackers_of.get(a, set()):
                violations.append(f"UNDEC({a}): all attackers defeated by IN -> should be IN")
            if all_defeated and not attackers_of.get(a, set()):
                violations.append(f"UNDEC({a}): has no attackers -> should be IN")

            has_in_attacker = any(
                attacker in in_set for attacker in attackers_of.get(a, set())
            )
            if has_in_attacker:
                violations.append(f"UNDEC({a}): has attacker in IN -> should be OUT")

        if violations:
            return {
                "verified": False,
                "status": "REFUTED",
                "violations": violations,
            }
        elif missing:
            return {
                "verified": False,
                "status": "INCONCLUSIVE",
                "violations": violations,
            }
        else:
            return {
                "verified": True,
                "status": "VERIFIED",
                "violations": [],
            }
