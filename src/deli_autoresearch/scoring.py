"""P3 Research automation -- enhanced breakthrough scoring.

Introduces BreakthroughScore for multi-dimensional impact evaluation and
rank_breakthroughs() for weighted composite ranking of research candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BreakthroughScore:
    """Multi-dimensional score for a research breakthrough candidate.

    Fields:
        impact_depth: Depth of downstream impact (higher = deeper reach).
            Range: non-negative integer.
        novelty_ratio: How novel the approach is. Range: 0.0 (incremental) to 1.0 (radical).
        rigor_score: Formal rigor of the claimed result. Range: 0 (conjecture) to 10 (machine-checked).
    """

    impact_depth: int
    novelty_ratio: float
    rigor_score: int

    def __post_init__(self) -> None:
        """Validate value ranges on construction."""
        if self.impact_depth < 0:
            raise ValueError(
                f"impact_depth must be >= 0, got {self.impact_depth}"
            )
        if not (0.0 <= self.novelty_ratio <= 1.0):
            raise ValueError(
                f"novelty_ratio must be in [0.0, 1.0], got {self.novelty_ratio}"
            )
        if not (0 <= self.rigor_score <= 10):
            raise ValueError(
                f"rigor_score must be in [0, 10], got {self.rigor_score}"
            )


@dataclass
class ScoredBreakthrough:
    """A research breakthrough annotated with its multi-dimensional score."""

    theorem_id: str
    proposition: str
    score: BreakthroughScore
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# Default weights for the three dimensions.
# impact_depth is the strongest signal (drives practical unlocks),
# novelty_ratio rewards non-incremental work,
# rigor_score ensures formal quality counts.
DEFAULT_WEIGHTS = {
    "impact_depth": 0.5,
    "novelty_ratio": 0.3,
    "rigor_score": 0.2,
}


def composite_score(
    score: BreakthroughScore,
    weights: dict[str, float] | None = None,
) -> float:
    """Compute a single weighted composite score from a BreakthroughScore.

    Normalises each dimension to [0, 1] before applying weights.
    The composite is in [0.0, 1.0].

    Args:
        score: The three-dimensional score to reduce.
        weights: Optional per-dimension weights. Defaults to DEFAULT_WEIGHTS.

    Returns:
        Weighted composite value in [0.0, 1.0].
    """
    w = weights if weights is not None else DEFAULT_WEIGHTS

    # Normalise: impact_depth uses log1p scaling to avoid linear domination.
    norm_impact = min(1.0, _normalised_impact(score.impact_depth))
    norm_novelty = score.novelty_ratio  # already [0, 1]
    norm_rigor = score.rigor_score / 10.0  # scale [0, 10] -> [0, 1]

    composite = (
        w.get("impact_depth", 0.5) * norm_impact
        + w.get("novelty_ratio", 0.3) * norm_novelty
        + w.get("rigor_score", 0.2) * norm_rigor
    )
    return round(composite, 4)


def _normalised_impact(depth: int) -> float:
    """Map raw impact_depth to [0, 1] via log1p.

    log1p(0) = 0.0, log1p(100) ~ 4.61. We cap at depth=100 for normalisation
    and scale so depth=10 -> ~0.73, depth=50 -> ~0.85, depth=100 -> 1.0.
    """
    import math

    if depth <= 0:
        return 0.0
    # log1p(depth) / log1p(100) -- caps at 1.0 for depth=100+
    cap = 100
    raw = math.log1p(min(depth, cap)) / math.log1p(cap)
    return raw


def rank_breakthroughs(
    candidates: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
) -> list[ScoredBreakthrough]:
    """Rank a list of breakthrough candidates by weighted multi-dimensional score.

    Each candidate dict is expected to contain at minimum:
        theorem_id, proposition, impact_depth, novelty_ratio, rigor_score.

    Args:
        candidates: List of candidate dicts with score fields.
        weights: Optional per-dimension weights. Defaults to DEFAULT_WEIGHTS.

    Returns:
        List of ScoredBreakthrough instances sorted by composite score descending.
    """
    scored: list[ScoredBreakthrough] = []

    for c in candidates:
        bs = BreakthroughScore(
            impact_depth=int(c.get("impact_depth", 0)),
            novelty_ratio=float(c.get("novelty_ratio", 0.0)),
            rigor_score=int(c.get("rigor_score", 0)),
        )
        sb = ScoredBreakthrough(
            theorem_id=str(c.get("theorem_id", "")),
            proposition=str(c.get("proposition", "")),
            score=bs,
            depends_on=list(c.get("depends_on", [])),
            metadata={k: v for k, v in c.items()
                      if k not in ("theorem_id", "proposition",
                                   "impact_depth", "novelty_ratio",
                                   "rigor_score", "depends_on")},
        )
        scored.append(sb)

    # Sort by composite score descending, then by theorem_id for stability.
    scored.sort(
        key=lambda sb: (composite_score(sb.score, weights), sb.theorem_id),
        reverse=True,
    )
    return scored
