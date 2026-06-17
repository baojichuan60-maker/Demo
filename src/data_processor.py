"""
Utilities for loading, validating, and normalising raw survey data
before it is fed into the diagnostic engine.
"""

from typing import Any, Dict, List, Optional
import csv
import json
import io


def load_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc


def load_csv(raw: str) -> List[Dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw))
    return list(reader)


def validate_survey_row(row: Dict[str, Any], required_fields: Optional[List[str]] = None) -> List[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors: List[str] = []
    required = required_fields or ["domain", "dimension", "score"]

    for field in required:
        if field not in row or row[field] is None or str(row[field]).strip() == "":
            errors.append(f"Missing required field: '{field}'")

    if "score" in row and row["score"] not in (None, ""):
        try:
            score = float(row["score"])
            if not (1.0 <= score <= 5.0):
                errors.append(f"Score {score} out of range [1, 5]")
        except (TypeError, ValueError):
            errors.append(f"Score '{row['score']}' is not a number")

    return errors


def normalise_score(raw_score: float, src_min: float, src_max: float, dst_min: float = 1.0, dst_max: float = 5.0) -> float:
    """Linear re-scale from [src_min, src_max] to [dst_min, dst_max]."""
    if src_max == src_min:
        raise ValueError("src_min and src_max must differ")
    if raw_score < src_min or raw_score > src_max:
        raise ValueError(f"raw_score {raw_score} outside [{src_min}, {src_max}]")
    ratio = (raw_score - src_min) / (src_max - src_min)
    return dst_min + ratio * (dst_max - dst_min)


def aggregate_scores(scores: List[float], weights: Optional[List[float]] = None) -> float:
    if not scores:
        raise ValueError("scores list is empty")
    if weights is not None:
        if len(weights) != len(scores):
            raise ValueError("scores and weights must have the same length")
        if any(w < 0 for w in weights):
            raise ValueError("weights must be non-negative")
        total_weight = sum(weights)
        if total_weight == 0:
            raise ValueError("total weight cannot be zero")
        return sum(s * w for s, w in zip(scores, weights)) / total_weight
    return sum(scores) / len(scores)


def detect_outliers(scores: List[float], z_threshold: float = 2.0) -> List[int]:
    """Return indices of scores that are statistical outliers (|z| > threshold)."""
    if len(scores) < 2:
        return []
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = variance ** 0.5
    if std == 0:
        return []
    return [i for i, s in enumerate(scores) if abs(s - mean) / std > z_threshold]


def merge_survey_batches(batches: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Concatenate multiple survey batches, de-duplicating by (domain, dimension)."""
    seen = set()
    merged = []
    for batch in batches:
        for row in batch:
            key = (row.get("domain"), row.get("dimension"))
            if key not in seen:
                seen.add(key)
                merged.append(row)
    return merged
