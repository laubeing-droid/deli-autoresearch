"""Phase F4: AutoResearch Running Rules for Deli AutoResearch.

Each research task must comply with these constraints:
1. Verification MUST be against formal payload bound to current claim
2. Each task must include: opposite hypothesis, counterexample search,
   theorem decomposition, implementation mapping, independent verification, tail pass
3. Model-generated / derived content cannot alone constitute a finding
4. Only Lean proof, Z3 UNSAT, reproducible experiment, or juris exact-payload
   test counts as strong evidence
5. Continuous stall allows pivot but not terminology-only recycling
6. Each direction has a max iteration cap; BLOCKED after exceeded
7. Alternative semantics (preferred, stage, CF2, semiring) are independent tasks
   only — never substitute Grounded correctness or alter production output
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AutoResearchConstraints:
    """Rules enforced on every Deli AutoResearch exploration task."""
    max_iterations_per_direction: int = 5
    required_directions: list[str] = field(default_factory=lambda: [
        "opposite_hypothesis",
        "counterexample_search",
        "theorem_decomposition",
        "implementation_mapping",
        "independent_verification",
        "tail_pass",
    ])
    strong_evidence_kinds: list[str] = field(default_factory=lambda: [
        "lean_proof",
        "z3_unsat",
        "reproducible_experiment",
        "juris_exact_payload_test",
    ])
    forbidden_standalone_kinds: list[str] = field(default_factory=lambda: [
        "model_generated",
        "derived",
    ])
    alternative_semantics: list[str] = field(default_factory=lambda: [
        "preferred",
        "stage",
        "CF2",
        "semiring",
    ])

    def validate_task_spec(self, task_spec: dict[str, Any]) -> list[str]:
        """Check that a task spec complies with all running rules."""
        errors: list[str] = []

        # Rule 1: verification must be claim-bound
        if not task_spec.get("formal_payload"):
            errors.append("Missing formal_payload — verification not claim-bound")

        # Rule 2: required direction types must be present
        directions = task_spec.get("directions", [])
        dir_types = {d.get("strategy_type", "") for d in directions}
        missing = set(self.required_directions) - dir_types
        if missing:
            errors.append(f"Missing required directions: {missing}")

        # Rule 3: derived/model_generated cannot be standalone
        for finding in task_spec.get("findings", []):
            source = finding.get("source_kind", "")
            if source in self.forbidden_standalone_kinds:
                supporting = finding.get("supporting_evidence", [])
                strong = [s for s in supporting
                         if s.get("source_kind") in self.strong_evidence_kinds]
                if not strong:
                    errors.append(
                        f"Finding from {source} has no strong supporting evidence"
                    )

        # Rule 7: alternative semantics must be independent tasks
        for direction in directions:
            stype = direction.get("strategy_type", "")
            if stype in self.alternative_semantics:
                if not task_spec.get("is_alternative_semantics_experiment"):
                    errors.append(
                        f"Alternative semantics {stype} must be an independent task"
                    )

        return errors

    def apply_rules(self, task_spec: dict[str, Any]) -> dict[str, Any]:
        """Apply all running rules to a task spec, returning annotated spec."""
        errors = self.validate_task_spec(task_spec)
        return {
            **task_spec,
            "constraints_applied": True,
            "constraints_version": "F4-1.0",
            "validation_errors": errors,
            "compliant": len(errors) == 0,
        }


# Pre-built task templates
G9A_TASK_TEMPLATE: dict[str, Any] = {
    "task_id": "g9a-grounded-proof",
    "template_type": "legal_proof",
    "formal_payload": {
        "verification_type": "grounded_extension",
        "claims": [],
        "attacks": [],
    },
    "directions": [
        {"strategy_type": "opposite_hypothesis",
         "summary": "Assume grounded extension is NOT unique; search for counterexample"},
        {"strategy_type": "counterexample_search",
         "summary": "Generate attack graphs where F iteration produces different results"},
        {"strategy_type": "theorem_decomposition",
         "summary": "Prove: F monotone => F^k(∅) monotone => termination => unique fixed point"},
        {"strategy_type": "implementation_mapping",
         "summary": "Verify Python grounded_extension matches Lean DungAAF.groundedExtension"},
        {"strategy_type": "independent_verification",
         "summary": "Run Z3 bounded model checking on generated graphs vs Lean specification"},
        {"strategy_type": "tail_pass",
         "summary": "Final verification: no counterexample found, all tests pass"},
    ],
    "max_iterations_per_direction": 5,
    "max_iterations": 30,
    "target_validated_findings": 3,
}

G10_TASK_TEMPLATE: dict[str, Any] = {
    "task_id": "g10-banach-multidim",
    "template_type": "legal_proof",
    "formal_payload": {
        "verification_type": "banach_contraction",
        "matrix": [],
        "norm_type": "max",
        "threshold": 1.0,
    },
    "directions": [
        {"strategy_type": "opposite_hypothesis",
         "summary": "Assume there exists non-contractive weighting"},
        {"strategy_type": "counterexample_search",
         "summary": "Generate random block matrices, test contraction failure"},
        {"strategy_type": "theorem_decomposition",
         "summary": "Prove: weighted max-norm contraction exists for block-triangular coupling"},
        {"strategy_type": "implementation_mapping",
         "summary": "Verify banach_verifier.py spectral_radius_ub matches linear algebra theorem"},
        {"strategy_type": "independent_verification",
         "summary": "Compare with NumPy eigenvalue computation"},
        {"strategy_type": "tail_pass",
         "summary": "Confirm no counterexample breaks contraction claim"},
    ],
    "max_iterations_per_direction": 5,
    "max_iterations": 30,
    "target_validated_findings": 2,
}
