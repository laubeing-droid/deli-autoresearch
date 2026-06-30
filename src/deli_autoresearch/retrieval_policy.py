"""Retrieval admission policy bound to an approved source registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .source_registry import APPROVED, PROPOSED, REJECTED, SourceRegistry


@dataclass(frozen=True)
class RetrievalDecision:
    """Policy result that separates retrieval from source candidacy."""

    source_id: str
    action: str
    allowed: bool
    reason: str
    source_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class RetrievalPolicy:
    """Allow only approved registry entries into retrieval."""

    def __init__(self, registry: SourceRegistry) -> None:
        self.registry = registry

    def decide(self, source_id: str, *, channel: str = "registry") -> RetrievalDecision:
        if channel == "open_web":
            return RetrievalDecision(
                source_id=source_id,
                action="source_candidate",
                allowed=False,
                reason="open_web may only create source_candidate records",
                source_status="unverified",
            )

        status = self.registry.status(source_id)
        if status == APPROVED:
            return RetrievalDecision(
                source_id=source_id,
                action="retrieve",
                allowed=True,
                reason="source is approved",
                source_status=status,
            )
        if status == PROPOSED:
            reason = "source is proposed but not approved"
        elif status == REJECTED:
            reason = "source is rejected"
        else:
            reason = "source is not registered"
        return RetrievalDecision(
            source_id=source_id,
            action="deny",
            allowed=False,
            reason=reason,
            source_status=status,
        )

    def filter_retrievable(self, source_ids: list[str]) -> list[str]:
        """Return only source ids that the policy allows for retrieval."""

        return [source_id for source_id in source_ids if self.decide(source_id).allowed]
