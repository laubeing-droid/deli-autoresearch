"""R1: Cross-repo integration tests — real end-to-end Deli <-> juris-calculus bridge."""
import pathlib, sys, json, pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from deli_autoresearch.juris_calculus_bridge import JurisCalculusBridge, BridgeResult
from deli_autoresearch.juris_calculus_backend import JurisCalculusBackend
from deli_autoresearch.agent_backend_codex import MockAgentBackend
from deli_autoresearch.canonical_fixture import CanonicalTestSuite
from deli_autoresearch.certificate_payload import GroundedExtensionCertificate
from deli_autoresearch.independent_checker import IndependentCheckerRegistry
from deli_autoresearch.lean_manifest import LeanManifest
from deli_autoresearch.lean_refinement import LeanRefinementBridge
from deli_autoresearch.models import (
    VERIFICATION_STATUS_PROVED, VERIFICATION_STATUS_REFUTED,
    VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE, VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
    VERIFICATION_STATUS_ERROR,
)

JURIS_ROOT = r"D:\Codex\juris-calculus"


class TestCrossRepoIntegration:
    """Real end-to-end: Deli formal payload -> juris-calculus -> verified verdict."""

    @classmethod
    def setup_class(cls):
        cls.bridge = JurisCalculusBridge(JURIS_ROOT)
        cls.backend = JurisCalculusBackend(
            MockAgentBackend(), JURIS_ROOT
        )

    # --- Bridge-level tests ---

    def test_bridge_dispatches_real_grounded(self):
        """Deli issues actual formal payload, juris-calculus evaluates it."""
        claims = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        attacks = [("A", "B"), ("B", "C")]
        result = self.bridge.run_test_case(
            "dag_linear", claims, attacks,
            expected_accepted={"A", "C"},
        )
        assert result.passed
        assert result.derived_bound > 0
        assert result.converged
        assert not result.truncated
        assert len(result.engine_commit) == 40

    def test_bridge_cycle_graph(self):
        """Mutual attack cycle: both undecided."""
        claims = [{"id": "A"}, {"id": "B"}]
        attacks = [("A", "B"), ("B", "A")]
        result = self.bridge.run_test_case(
            "bidirectional", claims, attacks,
            expected_undecided={"A", "B"},
        )
        assert result.passed
        assert result.converged
        assert not result.truncated

    def test_bridge_new_fields_present(self):
        """All v3.0 fields are consumed and non-None for any run."""
        claims = [{"id": "X"}]
        attacks = []
        result = self.bridge.run_test_case("singleton", claims, attacks)
        assert result.derived_bound > 0
        assert result.converged is True
        assert result.truncated is False
        assert result.engine_commit != ""
        assert result.protocol_version == "1.0"

    def test_bridge_all_builtin_cases_pass(self):
        """Full regression suite: 14 case types."""
        report = self.bridge.run_full_regression()
        assert report.total >= 14
        assert report.failed == 0
        assert report.all_passed

    def test_independent_checker_verifies_canonical_case(self):
        case = next(c for c in CanonicalTestSuite.grounded_extension_cases() if c.name == "singleton")
        raw = self.bridge.run_grounded_extension(case.claims, case.attacks)
        cert = GroundedExtensionCertificate.from_engine_result(
            case.claims,
            case.attacks,
            raw,
            engine_commit=self.bridge._get_commit_sha(),
        )
        registry = IndependentCheckerRegistry(juris_root=JURIS_ROOT)
        result = registry.verify_all(cert)
        assert result["overall"] == "verified"

    def test_lean_manifest_uses_formal_release_manifest(self):
        manifest = LeanManifest()
        assert ("D:" + "\\Claude") not in str(manifest.path)
        assert manifest.total_theorems == 100
        assert len({item.get("name") for item in manifest.complete_theorems()}) == 94
        assert manifest.build_status == "PASS"
        assert manifest.is_strong_evidence("grounded_is_least_fixed_point")

    def test_refinement_bridge_runs_cross_repo_regression(self):
        refinement = LeanRefinementBridge(juris_root=JURIS_ROOT)
        report = refinement.run_cross_repo_regression()
        assert report.total >= 14
        assert report.failed == 0
        assert report.all_passed

    # --- Backend-level: fail-closed gates ---

    def test_backend_normal_case_proved(self):
        """Normal converged path produces PROVED."""
        prompt = {
            "claim_id": "test-001",
            "claim": "A attacks B so A is accepted",
            "formal_payload": {
                "claims": [{"id": "A"}, {"id": "B"}],
                "attacks": [("A", "B")],
                "expected_properties": {"expected_accepted": ["A"]},
            },
            "verification_type": "grounded_extension",
            "claim_bound_contract": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        payload = envelope.payload
        assert payload["verification_status"] == VERIFICATION_STATUS_PROVED
        assert payload["verdict"] == "validated"
        assert "converged" in str(payload)
        assert "engine_commit" in payload
        assert payload["independent_checker"]["overall"] == "verified"

    def test_backend_missing_expected_fails(self):
        """If expected properties don't match, must REFUTE."""
        prompt = {
            "claim_id": "test-002",
            "formal_payload": {
                "claims": [{"id": "A"}, {"id": "B"}],
                "attacks": [("A", "B")],
                "expected_properties": {"expected_accepted": ["B"]},  # wrong!
            },
            "verification_type": "grounded_extension",
            "claim_bound_contract": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        assert envelope.payload["verification_status"] == VERIFICATION_STATUS_REFUTED

    def test_backend_claim_bound_mismatch_fails_closed(self):
        """Claim-bound path must reject mismatched verification_type."""
        prompt = {
            "claim_id": "test-002b",
            "formal_payload": {
                "claims": [{"id": "A"}],
                "attacks": [("A", "B")],
            },
            "verification_type": "smt_logic",
            "claim_bound_contract": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        payload = envelope.payload
        assert payload["verification_status"] == VERIFICATION_STATUS_BACKEND_UNAVAILABLE
        assert payload["fail_reason"] == "verification_type_mismatch"

    # --- Version protocol ---

    def test_engine_commit_recorded(self):
        """Verification artifact records juris-calculus commit SHA."""
        prompt = {
            "claim_id": "test-003",
            "formal_payload": {
                "claims": [{"id": "A"}],
                "attacks": [("A", "B")],
            },
            "verification_type": "grounded_extension",
            "claim_bound_contract": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        commit = envelope.payload.get("engine_commit", "")
        assert len(commit) == 40, f"Expected 40-char SHA, got: {commit}"

    def test_protocol_version_present(self):
        """All verification payloads carry protocol_version."""
        prompt = {
            "claim_id": "test-004",
            "formal_payload": {
                "claims": [{"id": "X"}],
                "attacks": [("X", "Y")],
            },
            "verification_type": "grounded_extension",
            "claim_bound_contract": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        assert envelope.payload.get("protocol_version") == "1.0"

    # --- Stress: 150-node test ---

    def test_large_graph_stress(self):
        """150-node DAG converges and all new fields valid."""
        claims = [{"id": f"A{i}"} for i in range(150)]
        # Chain: A0 -> A1 -> A2 -> ...
        attacks = [(f"A{i}", f"A{i+1}") for i in range(149)]
        result = self.bridge.run_test_case("large_150", claims, attacks)
        assert result.passed
        assert result.derived_bound >= 150
        assert result.converged
        assert not result.truncated
        assert result.iterations <= result.derived_bound

    def test_backend_independent_checker_refutation_fails_closed(self):
        prompt = {
            "claim_id": "test-005",
            "formal_payload": {
                "claims": [{"id": "A"}],
                "attacks": [],
                "expected_properties": {"expected_accepted": ["A"]},
            },
            "verification_type": "grounded_extension",
            "claim_bound_contract": True,
        }
        self.backend.independent_checker.verify_all = lambda cert: {
            "overall": "rejected",
            "checker_results": {"forced": {"status": "REFUTED"}},
            "violations": ["forced refutation"],
        }
        envelope = self.backend.run_verification("task-test", prompt)
        assert envelope.payload["verification_status"] == VERIFICATION_STATUS_ERROR
        assert envelope.payload["fail_reason"] == "independent_checker_refuted"


    # --- Litigation certificate cross-repo ---

    def test_bridge_generates_litigation_certificate_with_minimal_witnesses(self):
        claims = [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}]
        attacks = [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]
        cert = self.bridge.generate_litigation_certificate("A", claims, attacks)
        assert cert["label"] == "IN"
        assert cert["attackers"] == ["B", "C"]
        assert cert["minimal_witnesses"] == ["D"]
        assert cert["witnesses"] == ["D"]
        assert cert["proof_depth"] == 1
        assert cert["defense_paths"] == [
            {"target": "A", "attacker": "B", "defenders": ["D"]},
            {"target": "A", "attacker": "C", "defenders": ["D"]},
        ]

    def test_bridge_generates_undecided_certificate_with_correct_witnesses(self):
        claims = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        attacks = [("A", "B"), ("B", "A"), ("B", "C")]
        cert = self.bridge.generate_litigation_certificate("C", claims, attacks)
        assert cert["label"] == "UNDEC"
        assert cert["attackers"] == ["B"]
        assert cert["witnesses"] == ["B"]

    def test_bridge_proof_depth_zero_for_unattacked_in(self):
        claims = [{"id": "X"}]
        attacks = []
        cert = self.bridge.generate_litigation_certificate("X", claims, attacks)
        assert cert["label"] == "IN"
        assert cert["attackers"] == []
        assert cert["proof_depth"] == 0
        assert cert["minimal_witnesses"] == []

    def test_bridge_out_argument_proof_depth_one(self):
        claims = [{"id": "A"}, {"id": "B"}]
        attacks = [("A", "B")]
        cert = self.bridge.generate_litigation_certificate("B", claims, attacks)
        assert cert["label"] == "OUT"
        assert cert["attackers"] == ["A"]
        assert cert["proof_depth"] == 1


    # --- Horn completeness cross-repo ---

    def test_bridge_minimal_support_computes_backward_closure(self):
        """Horn minimal support set traverses backward dependency chain."""
        initial = {"fact_a", "fact_b"}
        rules = [
            {"head": "C", "body": ["fact_a", "fact_b"]},
            {"head": "D", "body": ["C"]},
        ]
        result = self.bridge.compute_horn_minimal_support("D", initial, rules)
        assert result == {"fact_a", "fact_b"}

    def test_bridge_minimal_rebuttal_finds_hitting_set(self):
        initial = {"fact_a", "fact_b", "fact_c"}
        rules = [
            {"head": "X", "body": ["fact_a", "fact_b"]},
            {"head": "X", "body": ["fact_a", "fact_c"]},
        ]
        result = self.bridge.compute_horn_minimal_rebuttal("X", initial, rules)
        assert len(result) >= 1
        assert "fact_a" in result

    def test_bridge_missing_evidence_detects_gap(self):
        initial = {"fact_a"}
        rules = [{"head": "C", "body": ["fact_a", "fact_b"]}]
        report = self.bridge.compute_horn_missing_evidence("C", initial, rules)
        assert report["missing_facts"] == ["fact_b"]

    def test_bridge_rule_impact_propagates_downstream(self):
        initial = {"a", "b"}
        rules = [
            {"head": "C", "body": ["a", "b"], "id": "r_c"},
            {"head": "D", "body": ["C"], "id": "r_d"},
        ]
        impact = self.bridge.analyze_horn_rule_impact("r_c", rules, initial)
        assert impact["total_affected"] == 2
        assert impact["severity"] == "minor"


    # --- P2 batch litigation integration ---

    def test_backend_runs_batch_litigation_pipeline(self):
        """Backend batch litigation runs full Horn->AAF->grounded pipeline."""
        cases = [
            {
                "case_id": "chain",
                "facts": ["a", "b"],
                "horn_rules": [
                    {"head": "C", "body": ["a", "b"]},
                    {"head": "D", "body": ["C"]},
                ],
                "target_claims": ["C", "D"],
            }
        ]
        result = self.backend.run_litigation_batch(cases)
        assert result["batch_report"]["all_passed"]
        assert result["batch_report"]["total_cases"] == 1
        case = result["batch_report"]["cases"][0]
        assert case["case_id"] == "chain"
        assert len(case["certificates"]) >= 1
        assert len(case["rule_impacts"]) >= 1
        assert case["certificates_count"] >= 1
        assert result["engine_commit"] != ""
        assert result["protocol_version"] == "1.0"

    def test_legal_proof_template_runs_batch_through_backend(self):
        """legal_proof template run_litigation_batch delegates to backend."""
        import sys, os
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
        from deli_autoresearch.template_runtime import TemplateRuntime
        rt = TemplateRuntime()
        legal = rt.get("legal_proof")
        cases = [
            {
                "case_id": "t1",
                "facts": ["x", "y"],
                "horn_rules": [{"head": "Z", "body": ["x", "y"]}],
                "target_claims": ["Z"],
            }
        ]
        result = legal.run_litigation_batch(self.backend, cases)
        assert result["batch_report"]["all_passed"]


    # --- P3 research automation ---

    def test_research_automation_ranks_breakthroughs(self):
        """P3 breakthrough scoring returns ranked candidates from jc."""
        import sys, os
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
        from deli_autoresearch.research_automation import run_research_automation
        report = run_research_automation(juris_root=JURIS_ROOT)
        assert len(report.breakthroughs) >= 10
        assert len(report.capability_map) >= 10
        assert report.benchmark_results.get("all_passed") is True
        assert report.top_priority != ""

    def test_research_automation_benchmark_replay_passes(self):
        """Standard benchmark cases all pass against current engine."""
        import sys, os
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
        from deli_autoresearch.research_automation import run_benchmark_replay
        result = run_benchmark_replay(juris_root=JURIS_ROOT)
        assert result["all_passed"]
        assert result["total_cases"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
