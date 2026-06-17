"""
Tests for src/diagnostic.py

Coverage gaps (intentional, to be improved):
  - SubDimension: score boundary validation not tested
  - Domain.maturity_label: labels for scores 1, 2, 4, 5 not tested
  - DiagnosticReport.strongest_domains: not tested
  - DiagnosticReport.domains_below_threshold with custom threshold: not tested
  - DiagnosticReport.score_gap_vs_benchmark: not tested
  - DiagnosticReport.to_dict: not tested
  - Empty domains / no sub-dimensions error paths: not tested
"""

import pytest
from src.diagnostic import SubDimension, Domain, DiagnosticReport


class TestSubDimension:
    def test_valid_creation(self):
        sd = SubDimension(name="user_research", score=3.5, weight=1.0)
        assert sd.score == 3.5
        assert sd.weight == 1.0

    def test_invalid_score_above_range(self):
        with pytest.raises(ValueError, match="Score must be between"):
            SubDimension(name="x", score=5.1)

    # Missing: test score below 1.0
    # Missing: test negative weight
    # Missing: test score exactly at boundaries (1.0 and 5.0)


class TestDomain:
    def _make_domain(self, scores, weights=None):
        sds = [
            SubDimension(name=f"dim_{i}", score=s, weight=(weights[i] if weights else 1.0))
            for i, s in enumerate(scores)
        ]
        return Domain(name="test_domain", sub_dimensions=sds)

    def test_weighted_score_equal_weights(self):
        domain = self._make_domain([2.0, 4.0])
        assert domain.weighted_score() == pytest.approx(3.0)

    def test_weighted_score_unequal_weights(self):
        domain = self._make_domain([1.0, 5.0], weights=[1.0, 3.0])
        assert domain.weighted_score() == pytest.approx(4.0)

    def test_maturity_label_score_3(self):
        domain = self._make_domain([3.0])
        assert domain.maturity_label() == "规范级"

    # Missing: maturity_label for scores 1, 2, 4, 5
    # Missing: weighted_score raises when no sub_dimensions


class TestDiagnosticReport:
    def _make_report(self, company="TestCo", domain_scores=None):
        domain_scores = domain_scores or {"market": 3.0, "design": 2.0, "quality": 4.0}
        report = DiagnosticReport(company=company)
        for name, score in domain_scores.items():
            sd = SubDimension(name="dim", score=score)
            report.domains[name] = Domain(name=name, sub_dimensions=[sd])
        return report

    def test_overall_score(self):
        report = self._make_report(domain_scores={"a": 2.0, "b": 4.0})
        assert report.overall_score() == pytest.approx(3.0)

    def test_weakest_domains_ordering(self):
        report = self._make_report(domain_scores={"a": 4.0, "b": 2.0, "c": 3.0})
        weakest = report.weakest_domains(n=2)
        assert weakest[0].name == "b"
        assert weakest[1].name == "c"

    def test_domains_below_threshold_default(self):
        report = self._make_report(domain_scores={"high": 4.0, "low": 2.5})
        below = report.domains_below_threshold()
        assert len(below) == 1
        assert below[0].name == "low"

    # Missing: strongest_domains
    # Missing: domains_below_threshold with custom threshold value
    # Missing: score_gap_vs_benchmark (positive gap, negative gap, missing domain key)
    # Missing: to_dict structure and values
    # Missing: overall_score raises ValueError when domains is empty
