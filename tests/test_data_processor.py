"""
Tests for src/data_processor.py

Coverage gaps (intentional, to be improved):
  - load_json: valid JSON not tested
  - load_csv: not tested at all
  - validate_survey_row: custom required_fields not tested; all-valid row not tested
  - normalise_score: edge cases (src_min==src_max, out-of-range) not tested
  - detect_outliers: fewer than 2 scores, zero std-dev not tested
  - merge_survey_batches: not tested at all
"""

import pytest
from src.data_processor import (
    load_json,
    validate_survey_row,
    normalise_score,
    aggregate_scores,
    detect_outliers,
)


class TestLoadJson:
    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_json("{bad json}")

    # Missing: test that valid JSON returns the correct dict
    # Missing: test empty string


class TestValidateSurveyRow:
    def test_missing_score_field(self):
        errors = validate_survey_row({"domain": "market", "dimension": "user_research"})
        assert any("score" in e for e in errors)

    def test_score_out_of_range(self):
        errors = validate_survey_row({"domain": "x", "dimension": "y", "score": "6"})
        assert any("out of range" in e for e in errors)

    def test_non_numeric_score(self):
        errors = validate_survey_row({"domain": "x", "dimension": "y", "score": "abc"})
        assert any("not a number" in e for e in errors)

    # Missing: fully valid row returns empty list
    # Missing: custom required_fields parameter
    # Missing: score exactly at boundary (1 and 5) is valid


class TestNormaliseScore:
    def test_midpoint_maps_correctly(self):
        result = normalise_score(50.0, src_min=0.0, src_max=100.0)
        assert result == pytest.approx(3.0)

    def test_min_maps_to_dst_min(self):
        result = normalise_score(0.0, src_min=0.0, src_max=100.0)
        assert result == pytest.approx(1.0)

    # Missing: max input maps to dst_max
    # Missing: src_min == src_max raises ValueError
    # Missing: raw_score out of [src_min, src_max] raises ValueError
    # Missing: custom dst_min / dst_max


class TestAggregateScores:
    def test_unweighted_average(self):
        assert aggregate_scores([1.0, 3.0, 5.0]) == pytest.approx(3.0)

    def test_weighted_average(self):
        assert aggregate_scores([1.0, 5.0], weights=[3.0, 1.0]) == pytest.approx(2.0)

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="empty"):
            aggregate_scores([])

    def test_mismatched_weights_raises(self):
        with pytest.raises(ValueError, match="same length"):
            aggregate_scores([1.0, 2.0], weights=[1.0])

    # Missing: all-zero weights raises ValueError
    # Missing: negative weight raises ValueError
    # Missing: single-element list


class TestDetectOutliers:
    def test_obvious_outlier_detected(self):
        scores = [3.0, 3.1, 2.9, 3.0, 5.0]
        outliers = detect_outliers(scores, z_threshold=1.5)
        assert 4 in outliers

    def test_no_outliers_in_uniform_list(self):
        scores = [3.0, 3.0, 3.0, 3.0]
        assert detect_outliers(scores) == []

    # Missing: fewer than 2 scores returns []
    # Missing: all identical scores (std=0) returns []
    # Missing: custom z_threshold boundary behaviour
