"""Tests for deli_autoresearch.scoring -- BreakthroughScore and rank_breakthroughs."""

from __future__ import annotations

import pytest

from deli_autoresearch.scoring import (
    BreakthroughScore,
    ScoredBreakthrough,
    composite_score,
    rank_breakthroughs,
)


class TestBreakthroughScore:
    """8 tests covering data validation, composite scoring, and ranking."""

    # ------------------------------------------------------------------
    # 1. Valid construction
    # ------------------------------------------------------------------

    def test_valid_score_construction(self) -> None:
        """A BreakthroughScore with all values in range constructs without error."""
        bs = BreakthroughScore(impact_depth=5, novelty_ratio=0.7, rigor_score=8)
        assert bs.impact_depth == 5
        assert bs.novelty_ratio == 0.7
        assert bs.rigor_score == 8

    # ------------------------------------------------------------------
    # 2. Boundary-value construction (minimum valid)
    # ------------------------------------------------------------------

    def test_minimum_boundary_values(self) -> None:
        """Zero values at the lower boundary construct successfully."""
        bs = BreakthroughScore(impact_depth=0, novelty_ratio=0.0, rigor_score=0)
        assert bs.impact_depth == 0
        assert bs.novelty_ratio == 0.0
        assert bs.rigor_score == 0

    def test_maximum_boundary_values(self) -> None:
        """Maximum allowed values construct successfully."""
        bs = BreakthroughScore(impact_depth=100, novelty_ratio=1.0, rigor_score=10)
        assert bs.impact_depth == 100
        assert bs.novelty_ratio == 1.0
        assert bs.rigor_score == 10

    # ------------------------------------------------------------------
    # 3. Invalid values raise ValueError
    # ------------------------------------------------------------------

    def test_negative_impact_depth_raises(self) -> None:
        """Negative impact_depth is rejected."""
        with pytest.raises(ValueError, match="impact_depth"):
            BreakthroughScore(impact_depth=-1, novelty_ratio=0.5, rigor_score=5)

    def test_novelty_ratio_below_zero_raises(self) -> None:
        """novelty_ratio < 0 is rejected."""
        with pytest.raises(ValueError, match="novelty_ratio"):
            BreakthroughScore(impact_depth=3, novelty_ratio=-0.1, rigor_score=5)

    def test_novelty_ratio_above_one_raises(self) -> None:
        """novelty_ratio > 1 is rejected."""
        with pytest.raises(ValueError, match="novelty_ratio"):
            BreakthroughScore(impact_depth=3, novelty_ratio=1.5, rigor_score=5)

    def test_rigor_score_out_of_range_raises(self) -> None:
        """rigor_score outside [0, 10] is rejected."""
        with pytest.raises(ValueError, match="rigor_score"):
            BreakthroughScore(impact_depth=3, novelty_ratio=0.5, rigor_score=11)

    # ------------------------------------------------------------------
    # 4. Composite score calculation
    # ------------------------------------------------------------------

    def test_composite_score_ordering(self) -> None:
        """Higher-performing scores produce higher composite scores."""
        low = BreakthroughScore(impact_depth=1, novelty_ratio=0.1, rigor_score=1)
        mid = BreakthroughScore(impact_depth=5, novelty_ratio=0.5, rigor_score=5)
        high = BreakthroughScore(impact_depth=50, novelty_ratio=1.0, rigor_score=10)

        cl = composite_score(low)
        cm = composite_score(mid)
        ch = composite_score(high)

        assert cl < cm < ch, f"Expected {cl} < {cm} < {ch}"

    # ------------------------------------------------------------------
    # 5. Ranking sorts by composite score descending
    # ------------------------------------------------------------------

    def test_rank_breakthroughs_sorts_descending(self) -> None:
        """rank_breakthroughs returns results sorted by composite score, highest first."""
        candidates = [
            {
                "theorem_id": "low",
                "proposition": "low impact",
                "impact_depth": 1,
                "novelty_ratio": 0.1,
                "rigor_score": 1,
            },
            {
                "theorem_id": "high",
                "proposition": "high impact",
                "impact_depth": 80,
                "novelty_ratio": 0.95,
                "rigor_score": 9,
            },
            {
                "theorem_id": "mid",
                "proposition": "mid impact",
                "impact_depth": 5,
                "novelty_ratio": 0.5,
                "rigor_score": 5,
            },
        ]

        ranked = rank_breakthroughs(candidates)
        assert len(ranked) == 3
        assert ranked[0].theorem_id == "high"
        assert ranked[1].theorem_id == "mid"
        assert ranked[2].theorem_id == "low"

        # Verify return type.
        assert all(isinstance(sb, ScoredBreakthrough) for sb in ranked)

    # ------------------------------------------------------------------
    # 6. Custom weights
    # ------------------------------------------------------------------

    def test_custom_weights_change_ranking(self) -> None:
        """Custom dimension weights affect the ranking order."""
        # Candidate A has better impact, B has better novelty+rigor.
        candidates = [
            {
                "theorem_id": "impact_heavy",
                "proposition": "big impact, moderate novelty+rigor",
                "impact_depth": 100,
                "novelty_ratio": 0.8,
                "rigor_score": 8,
            },
            {
                "theorem_id": "novel_rigorous",
                "proposition": "zero impact, high novelty+rigor",
                "impact_depth": 0,
                "novelty_ratio": 1.0,
                "rigor_score": 10,
            },
        ]

        # Default weights (impact=0.5, novelty=0.3, rigor=0.2): impact wins.
        default_ranked = rank_breakthroughs(candidates)
        assert default_ranked[0].theorem_id == "impact_heavy"

        # Flip weights: novelty=0.8 -> novel_rigorous should win.
        custom_weights = {"impact_depth": 0.1, "novelty_ratio": 0.8, "rigor_score": 0.1}
        custom_ranked = rank_breakthroughs(candidates, weights=custom_weights)
        assert custom_ranked[0].theorem_id == "novel_rigorous"

    # ------------------------------------------------------------------
    # 7. Empty input returns empty list
    # ------------------------------------------------------------------

    def test_rank_breakthroughs_empty_input(self) -> None:
        """Empty candidate list produces empty ranked list."""
        result = rank_breakthroughs([])
        assert result == []
        assert isinstance(result, list)

    # ------------------------------------------------------------------
    # 8. Missing fields default to zero
    # ------------------------------------------------------------------

    def test_missing_fields_default_to_zero(self) -> None:
        """Candidates with missing score fields default to 0 and still rank."""
        candidates = [
            {"theorem_id": "bare", "proposition": "no scores"},
        ]
        ranked = rank_breakthroughs(candidates)
        assert len(ranked) == 1
        assert ranked[0].score.impact_depth == 0
        assert ranked[0].score.novelty_ratio == 0.0
        assert ranked[0].score.rigor_score == 0

