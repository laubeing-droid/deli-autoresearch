"""Canonical AAF serialization — R4: Lean↔Python refinement bridge.

Defines the canonical JSON format for finite Dung AAFs.
Provides an executable Python oracle that wraps juris-calculus.
The Lean manifest provides the spec; this provides the implementation.
Automated differential testing connects the two.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


CANONICAL_FORMAT_VERSION = "1.0"


@dataclass
class CanonicalAAF:
    """Canonical finite Dung argumentation framework.

    Format:
    {
      "arguments": ["A", "B", "C"],
      "attacks": [["A", "B"], ["B", "C"]],
      "argument_order": ["A", "B", "C"]
    }

    Rules:
    - arguments: unique, non-empty strings
    - attacks: list of (source, target) pairs; both must be in arguments
    - argument_order: deterministic ordering for output reproducibility
    - self-attacks are allowed
    - duplicate attacks are deduplicated via set
    """
    arguments: list[str]
    attacks: list[tuple[str, str]]
    argument_order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": CANONICAL_FORMAT_VERSION,
            "arguments": self.arguments,
            "attacks": [list(a) for a in self.attacks],
            "argument_order": self.argument_order or self.arguments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanonicalAAF":
        args = data.get("arguments", [])
        attacks = [tuple(a) for a in data.get("attacks", [])]
        order = data.get("argument_order", args)
        # Validate all attack endpoints exist
        arg_set = set(args)
        for src, tgt in attacks:
            if src not in arg_set:
                raise ValueError(f"Attack source '{src}' not in arguments")
            if tgt not in arg_set:
                raise ValueError(f"Attack target '{tgt}' not in arguments")
        # Deduplicate attacks
        unique_attacks = list(dict.fromkeys(attacks))
        return cls(arguments=args, attacks=unique_attacks, argument_order=order)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, s: str) -> "CanonicalAAF":
        return cls.from_dict(json.loads(s))


class AAFGroundedOracle:
    """Executable oracle: computes grounded extension via juris-calculus engine.

    This is the Python reference implementation against which the Lean spec
    is differentially tested.
    """

    def __init__(self, juris_root: str) -> None:
        self.juris_root = juris_root
        self._grounded_fn = None

    def _ensure_import(self):
        if self._grounded_fn is not None:
            return self._grounded_fn
        import sys, importlib
        root_str = str(self.juris_root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        mod = importlib.import_module("compiler_core.argumentation")
        self._grounded_fn = mod.grounded_extension
        return self._grounded_fn

    def compute(self, aaf: CanonicalAAF | dict[str, Any]) -> dict[str, Any]:
        """Run grounded extension on the AAF and return full v3.0 result."""
        if isinstance(aaf, CanonicalAAF):
            claims = [{"id": a} for a in aaf.arguments]
            attacks = aaf.attacks
        else:
            claims = [{"id": a} for a in aaf.get("arguments", [])]
            attacks = [tuple(a) for a in aaf.get("attacks", [])]
        fn = self._ensure_import()
        return fn(claims, attacks)

    def labels(self, aaf: CanonicalAAF | dict[str, Any]) -> dict[str, list[str]]:
        """Return {in: [...], out: [...], undec: [...]} from grounded extension."""
        raw = self.compute(aaf)
        return {
            "in": raw.get("accepted", []),
            "out": raw.get("rejected", []),
            "undec": raw.get("undecided", []),
            "derived_bound": raw.get("derived_bound", 0),
            "converged": raw.get("convergent", False),
            "truncated": raw.get("truncated", False),
            "iterations": raw.get("iterations", 0),
        }


# Standard test cases for differential testing
STANDARD_TEST_CASES = [
    {
        "name": "empty",
        "aaf": {"arguments": [], "attacks": []},
        "expected_in": [],
        "expected_undec": [],
    },
    {
        "name": "singleton",
        "aaf": {"arguments": ["A"], "attacks": []},
        "expected_in": ["A"],
        "expected_undec": [],
    },
    {
        "name": "self_attack",
        "aaf": {"arguments": ["A"], "attacks": [["A", "A"]]},
        "expected_in": [],
        "expected_undec": ["A"],
    },
    {
        "name": "dag_chain_3",
        "aaf": {"arguments": ["A", "B", "C"], "attacks": [["A", "B"], ["B", "C"]]},
        "expected_in": ["A", "C"],
        "expected_undec": [],
    },
    {
        "name": "mutual_attack",
        "aaf": {"arguments": ["A", "B"], "attacks": [["A", "B"], ["B", "A"]]},
        "expected_in": [],
        "expected_undec": ["A", "B"],
    },
    {
        "name": "odd_cycle_3",
        "aaf": {"arguments": ["A", "B", "C"], "attacks": [["A", "B"], ["B", "C"], ["C", "A"]]},
        "expected_in": [],
        "expected_undec": ["A", "B", "C"],
    },
    {
        "name": "even_cycle_4",
        "aaf": {"arguments": ["A", "B", "C", "D"],
                 "attacks": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]},
        "expected_in": [],
        "expected_undec": ["A", "B", "C", "D"],
    },
    {
        "name": "dag_attacks_cycle",
        "aaf": {"arguments": ["P", "Q", "X", "Y"],
                 "attacks": [["P", "X"], ["X", "Y"], ["Y", "X"]]},
        "expected_in": ["P", "Y"],
        "expected_undec": [],
    },
]