"""Tests for demo classifier — SPEC-010 TASK-010-001."""
import pytest
from deli_autoresearch.demo.classifier import classify_score


class TestClassifyScore:
    def test_below_zero_raises(self):
        with pytest.raises(ValueError):
            classify_score(-1)

    def test_above_100_raises(self):
        with pytest.raises(ValueError):
            classify_score(101)

    def test_fail_zone(self):
        assert classify_score(20) == "FAIL"

    def test_pass_zone(self):
        assert classify_score(55) == "PASS"

    def test_distinction_zone(self):
        assert classify_score(85) == "DISTINCTION"

    def test_boundary_0(self):
        assert classify_score(0) == "FAIL"

    def test_boundary_40(self):
        assert classify_score(40) == "PASS"

    def test_boundary_70(self):
        assert classify_score(70) == "DISTINCTION"

    def test_boundary_100(self):
        assert classify_score(100) == "DISTINCTION"
