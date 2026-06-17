"""
Converts a DiagnosticReport into human-readable output formats.
"""

from typing import List
from src.diagnostic import DiagnosticReport, Domain

_IMPROVEMENT_THRESHOLD = 3.0
_HIGH_SCORE = 4.0


def format_score(score: float, decimals: int = 2) -> str:
    return f"{score:.{decimals}f}"


def domain_summary_line(name: str, domain: Domain) -> str:
    score = domain.weighted_score()
    label = domain.maturity_label()
    bar = _score_bar(score)
    return f"{name:<25} {bar}  {format_score(score)} ({label})"


def _score_bar(score: float, width: int = 10) -> str:
    filled = round((score / 5.0) * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def render_text_report(report: DiagnosticReport) -> str:
    lines: List[str] = []
    lines.append(f"=== R&D Capability Diagnostic: {report.company} ===")
    lines.append(f"Overall Score: {format_score(report.overall_score())} / 5.00")
    lines.append("")
    lines.append("Domain Breakdown:")
    lines.append("-" * 55)
    for name, domain in report.domains.items():
        lines.append(domain_summary_line(name, domain))
    lines.append("-" * 55)

    weak = report.domains_below_threshold(_IMPROVEMENT_THRESHOLD)
    if weak:
        lines.append("")
        lines.append("Priority Improvement Areas:")
        for domain in weak:
            lines.append(f"  • {domain.name} ({format_score(domain.weighted_score())})")

    return "\n".join(lines)


def render_comparison_report(company: DiagnosticReport, benchmark: DiagnosticReport) -> str:
    lines: List[str] = []
    lines.append(f"=== Benchmark Comparison: {company.company} vs {benchmark.company} ===")
    gaps = company.score_gap_vs_benchmark(benchmark)
    for domain_key, gap in sorted(gaps.items(), key=lambda x: x[1]):
        sign = "+" if gap >= 0 else ""
        lines.append(f"  {domain_key:<25} gap: {sign}{format_score(gap)}")
    return "\n".join(lines)


def render_json_report(report: DiagnosticReport) -> str:
    import json
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
