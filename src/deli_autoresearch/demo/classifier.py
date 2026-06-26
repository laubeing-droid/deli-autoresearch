"""Demo classifier for SPEC-010 control chain verification."""


def classify_score(score: int) -> str:
    """Classify a numeric score into a grade band.

    Args:
        score: Integer score in range [0, 100].

    Returns:
        "FAIL" for 0-39, "PASS" for 40-69, "DISTINCTION" for 70-100.

    Raises:
        ValueError: If score is outside [0, 100].
    """
    if score < 0 or score > 100:
        raise ValueError(f"score must be in [0, 100], got {score}")
    if score < 40:
        return "FAIL"
    if score < 70:
        return "PASS"
    return "DISTINCTION"
