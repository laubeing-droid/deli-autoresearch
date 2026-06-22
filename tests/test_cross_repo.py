"""R1: Cross-repo integration tests — real end-to-end Deli <-> juris-calculus bridge."""
import pathlib, sys, json, pytest

sys.path.insert(0, r"D:\Claude\数学证明自动研究\src")
from deli_autoresearch.juris_calculus_bridge import JurisCalculusBridge, BridgeResult
from deli_autoresearch.juris_calculus_backend import JurisCalculusBackend
from deli_autoresearch.agent_backend_codex import MockAgentBackend
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
            "run_local_engine": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        payload = envelope.payload
        assert payload["verification_status"] == VERIFICATION_STATUS_PROVED
        assert payload["verdict"] == "validated"
        assert "converged" in str(payload)
        assert "engine_commit" in payload

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
            "run_local_engine": True,
        }
        envelope = self.backend.run_verification("task-test", prompt)
        assert envelope.payload["verification_status"] == VERIFICATION_STATUS_REFUTED

    # --- Version protocol ---

    def test_engine_commit_recorded(self):
        """Verification artifact records juris-calculus commit SHA."""
        prompt = {
            "claim_id": "test-003",
            "formal_payload": {
                "claims": [{"id": "A"}],
                "attacks": [],
            },
            "verification_type": "grounded_extension",
            "run_local_engine": True,
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
                "attacks": [],
            },
            "verification_type": "grounded_extension",
            "run_local_engine": True,
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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
