"""
R&D Capability Diagnostic scoring engine.

Domains are scored 1-5. Each domain can have sub-dimensions, each also 1-5.
The domain score is the weighted average of its sub-dimension scores.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DOMAINS = [
    "market_insights",
    "product_definition",
    "technology_research",
    "appearance_design",
    "structure_design",
    "electronics_software",
    "atomization_taste",
    "quality_management",
    "supply_chain",
    "npi",
]

SCORE_LABELS = {
    1: "初始级",   # Initial
    2: "基础级",   # Basic
    3: "规范级",   # Standardised
    4: "优化级",   # Optimised
    5: "卓越级",   # Excellent
}


@dataclass
class SubDimension:
    name: str
    score: float
    weight: float = 1.0
    notes: str = ""

    def __post_init__(self):
        if not (1.0 <= self.score <= 5.0):
            raise ValueError(f"Score must be between 1 and 5, got {self.score}")
        if self.weight <= 0:
            raise ValueError(f"Weight must be positive, got {self.weight}")


@dataclass
class Domain:
    name: str
    sub_dimensions: List[SubDimension] = field(default_factory=list)

    def weighted_score(self) -> float:
        if not self.sub_dimensions:
            raise ValueError(f"Domain '{self.name}' has no sub-dimensions")
        total_weight = sum(sd.weight for sd in self.sub_dimensions)
        return sum(sd.score * sd.weight for sd in self.sub_dimensions) / total_weight

    def maturity_label(self) -> str:
        score = round(self.weighted_score())
        return SCORE_LABELS.get(score, "未知")


@dataclass
class DiagnosticReport:
    company: str
    domains: Dict[str, Domain] = field(default_factory=dict)

    def overall_score(self) -> float:
        if not self.domains:
            raise ValueError("Report has no domains")
        scores = [d.weighted_score() for d in self.domains.values()]
        return sum(scores) / len(scores)

    def weakest_domains(self, n: int = 3) -> List[Domain]:
        sorted_domains = sorted(self.domains.values(), key=lambda d: d.weighted_score())
        return sorted_domains[:n]

    def strongest_domains(self, n: int = 3) -> List[Domain]:
        sorted_domains = sorted(self.domains.values(), key=lambda d: d.weighted_score(), reverse=True)
        return sorted_domains[:n]

    def domains_below_threshold(self, threshold: float = 3.0) -> List[Domain]:
        return [d for d in self.domains.values() if d.weighted_score() < threshold]

    def score_gap_vs_benchmark(self, benchmark: "DiagnosticReport") -> Dict[str, float]:
        gaps = {}
        for key, domain in self.domains.items():
            if key in benchmark.domains:
                gaps[key] = domain.weighted_score() - benchmark.domains[key].weighted_score()
        return gaps

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "overall_score": round(self.overall_score(), 2),
            "domains": {
                name: {
                    "score": round(domain.weighted_score(), 2),
                    "maturity": domain.maturity_label(),
                    "sub_dimensions": [
                        {"name": sd.name, "score": sd.score, "weight": sd.weight}
                        for sd in domain.sub_dimensions
                    ],
                }
                for name, domain in self.domains.items()
            },
        }
