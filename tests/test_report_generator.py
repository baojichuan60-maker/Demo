"""
Tests for src/report_generator.py

Coverage gaps (intentional, to be improved):
  - _score_bar: not tested (private helper)
  - render_text_report: "Priority Improvement Areas" section not tested
  - render_comparison_report: not tested at all
  - render_json_report: not tested at all
  - format_score: custom decimals parameter not tested
"""

import pytest
from src.diagnostic import DiagnosticReport, Domain, SubDimension
from src.report_generator import format_score, domain_summary_line, render_text_report


def _make_report(company="ACME", domain_scores=None):
    domain_scores = domain_scores or {"market": 3.5}
    report = DiagnosticReport(company=company)
    for name, score in domain_scores.items():
        sd = SubDimension(name="dim", score=score)
        report.domains[name] = Domain(name=name, sub_dimensions=[sd])
    return report


class TestFormatScore:
    def test_default_two_decimals(self):
        assert format_score(3.0) == "3.00"

    def test_rounds_correctly(self):
        assert format_score(3.14159, decimals=2) == "3.14"

    # Missing: decimals=0
    # Missing: decimals=4


class TestDomainSummaryLine:
    def test_contains_score_and_label(self):
        domain = Domain(name="quality", sub_dimensions=[SubDimension(name="d", score=3.0)])
        line = domain_summary_line("quality", domain)
        assert "3.00" in line
        assert "规范级" in line

    # Missing: line format when score is 1 (lowest bar)
    # Missing: line format when score is 5 (full bar)


class TestRenderTextReport:
    def test_header_contains_company(self):
        report = _make_report(company="SMOORE")
        output = render_text_report(report)
        assert "SMOORE" in output

    def test_overall_score_present(self):
        report = _make_report(domain_scores={"a": 4.0})
        output = render_text_report(report)
        assert "4.00" in output

    # Missing: "Priority Improvement Areas" appears when a domain < 3.0
    # Missing: "Priority Improvement Areas" absent when all domains >= 3.0
    # Missing: render_comparison_report (not imported / not tested)
    # Missing: render_json_report output is valid JSON and matches to_dict()
