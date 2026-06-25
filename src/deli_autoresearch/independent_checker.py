"""Unified independent checker registry for grounded extension certificates."""

from __future__ import annotations

from typing import Any, Callable

from .certificate_payload import GroundedExtensionCertificate
from .certificate_verifier import CertificateVerifier
from .lean_manifest import DEFAULT_LEAN_MANIFEST_PATH, LeanManifest


CheckerFn = Callable[[GroundedExtensionCertificate], dict[str, Any]]


class IndependentCheckerRegistry:
    """Run all registered independent checkers and merge the verdicts."""

    def __init__(
        self,
        *,
        juris_root: str | None = None,
        manifest_path: str = DEFAULT_LEAN_MANIFEST_PATH,
    ) -> None:
        self._checkers: dict[str, CheckerFn] = {}
        self._manifest = LeanManifest(manifest_path)
        self.register("deductive", self._verify_deductive)
        self.register("lean_manifest", self._verify_lean_manifest)
        if juris_root:
            self._register_juris_checkers(juris_root)

    def register(self, name: str, fn: CheckerFn) -> None:
        self._checkers[name] = fn

    def verify_all(self, cert: GroundedExtensionCertificate) -> dict[str, Any]:
        checker_results: dict[str, dict[str, Any]] = {}
        violations: list[str] = []
        has_verified = False

        for name, checker in self._checkers.items():
            result = checker(cert)
            checker_results[name] = result
            status = result.get("status", "").lower()
            if status in {"refuted", "rejected"}:
                violations.extend(result.get("violations", []) or [f"{name} rejected"])
                return {
                    "overall": "rejected",
                    "checker_results": checker_results,
                    "violations": violations,
                }
            if status in {"verified", "pass", "sat-match"}:
                has_verified = True
            violations.extend(result.get("violations", []))

        overall = "verified" if has_verified else "inconclusive"
        return {
            "overall": overall,
            "checker_results": checker_results,
            "violations": violations,
        }

    def _verify_deductive(self, cert: GroundedExtensionCertificate) -> dict[str, Any]:
        verifier = CertificateVerifier()
        return verifier.verify(
            cert.arguments,
            cert.attacks,
            cert.claimed_in,
            cert.claimed_out,
            cert.claimed_undec,
        )

    def _verify_lean_manifest(self, cert: GroundedExtensionCertificate) -> dict[str, Any]:
        missing = [
            theorem
            for theorem in cert.lean_theorem_refs
            if not self._manifest.is_strong_evidence(theorem)
        ]
        if missing:
            return {
                "status": "REFUTED",
                "verified": False,
                "violations": [f"Lean manifest missing strong evidence: {missing}"],
            }
        return {"status": "VERIFIED", "verified": True, "violations": []}

    def _register_juris_checkers(self, juris_root: str) -> None:
        import importlib
        import sys

        if juris_root not in sys.path:
            sys.path.insert(0, juris_root)

        grounded_smt = importlib.import_module("compiler_core.grounded_smt_verifier")
        cert_mod = importlib.import_module("compiler_core.certificate_checker")
        GroundedSMTChecker = grounded_smt.GroundedSMTChecker
        GroundedINCertificate = cert_mod.GroundedINCertificate
        OUTCertificate = cert_mod.OUTCertificate
        UNDECCertificate = cert_mod.UNDECCertificate

        def verify_smt(cert: GroundedExtensionCertificate) -> dict[str, Any]:
            checker = GroundedSMTChecker()
            result = checker.verify_labelling(
                "grounded_certificate",
                [{"id": arg} for arg in cert.arguments],
                cert.attacks,
                set(cert.claimed_in),
                set(cert.claimed_undec),
            )
            if result.status in {"SKIP", "UNKNOWN"}:
                return {"status": "INCONCLUSIVE", "verified": False, "violations": [result.detail]}
            if result.passed:
                return {"status": "VERIFIED", "verified": True, "violations": []}
            return {"status": "REFUTED", "verified": False, "violations": [result.detail]}

        def verify_juris_certificates(cert: GroundedExtensionCertificate) -> dict[str, Any]:
            aaf = (tuple(cert.arguments), tuple(cert.attacks))
            violations: list[str] = []
            acceptance_iteration = self._acceptance_iterations(cert.arguments, cert.attacks)
            for arg in cert.claimed_in:
                if not GroundedINCertificate(arg, acceptance_iteration.get(arg, 1)).verify(aaf):
                    violations.append(f"GroundedINCertificate failed for {arg}")
            for arg in cert.claimed_out:
                attackers = [src for src, tgt in cert.attacks if tgt == arg and src in cert.claimed_in]
                if not attackers:
                    violations.append(f"OUT certificate missing IN attacker for {arg}")
                    continue
                attacker = attackers[0]
                out_cert = OUTCertificate(
                    argument_id=arg,
                    in_attacker=attacker,
                    attacker_in_cert=GroundedINCertificate(attacker, acceptance_iteration.get(attacker, 1)),
                )
                if not out_cert.verify(aaf):
                    violations.append(f"OUTCertificate failed for {arg}")
            for arg in cert.claimed_undec:
                if not UNDECCertificate(arg).verify(aaf):
                    violations.append(f"UNDECCertificate failed for {arg}")
            if violations:
                return {"status": "REFUTED", "verified": False, "violations": violations}
            return {"status": "VERIFIED", "verified": True, "violations": []}

        self.register("smt", verify_smt)
        self.register("juris_certificate", verify_juris_certificates)

    @staticmethod
    def _acceptance_iterations(arguments: list[str], attacks: list[tuple[str, str]]) -> dict[str, int]:
        arg_set = list(arguments)
        attack_set = set(attacks)
        grounded: set[str] = set()
        accepted_at: dict[str, int] = {}
        for iteration in range(1, len(arg_set) + 2):
            newly: set[str] = set()
            for arg in arg_set:
                if arg in grounded:
                    continue
                attackers = {src for src, tgt in attack_set if tgt == arg}
                if not attackers:
                    newly.add(arg)
                elif all(any((defender, attacker) in attack_set for defender in grounded) for attacker in attackers):
                    newly.add(arg)
            if not newly:
                break
            for arg in newly:
                accepted_at[arg] = iteration
            grounded |= newly
        return accepted_at
