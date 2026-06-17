# Test Coverage Analysis

## Current State

Running `pytest --cov=src --cov-report=term-missing` produces:

| Module | Statements | Missed | Coverage |
|---|---|---|---|
| `src/diagnostic.py` | 52 | 11 | **79%** |
| `src/data_processor.py` | 65 | 16 | **75%** |
| `src/report_generator.py` | 42 | 13 | **69%** |
| **Total** | **159** | **40** | **75%** |

All 25 existing tests pass. The gaps below represent concrete lines that are currently uncovered.

---

## Priority Improvement Areas

### 1. `src/diagnostic.py` — 79% (11 lines missed)

**Uncovered paths and what to add:**

#### a) `SubDimension` validation boundaries (lines 36–37)
Score must be in `[1, 5]` and weight must be positive. The below-range case and negative-weight case are never triggered.

```python
# Add to TestSubDimension:
def test_score_below_range_raises(self):
    with pytest.raises(ValueError, match="Score must be between"):
        SubDimension(name="x", score=0.9)

def test_score_at_exact_boundaries_valid(self):
    SubDimension(name="x", score=1.0)   # should not raise
    SubDimension(name="x", score=5.0)   # should not raise

def test_negative_weight_raises(self):
    with pytest.raises(ValueError, match="Weight must be positive"):
        SubDimension(name="x", score=3.0, weight=-1.0)
```

#### b) `Domain.weighted_score` — empty sub-dimensions error (line 44)
```python
def test_no_sub_dimensions_raises(self):
    domain = Domain(name="empty")
    with pytest.raises(ValueError, match="no sub-dimensions"):
        domain.weighted_score()
```

#### c) `Domain.maturity_label` — only "规范级" (score 3) is tested (line 54)
Scores 1, 2, 4, and 5 map to different labels and are completely untested.

```python
@pytest.mark.parametrize("score,expected", [
    (1.0, "初始级"),
    (2.0, "基础级"),
    (4.0, "优化级"),
    (5.0, "卓越级"),
])
def test_maturity_labels(self, score, expected):
    domain = self._make_domain([score])
    assert domain.maturity_label() == expected
```

#### d) `DiagnosticReport.strongest_domains` — never called (lines 79–80)
Mirror of the existing `weakest_domains` test.

#### e) `DiagnosticReport.score_gap_vs_benchmark` — fully uncovered (lines 86–90)
This is business-critical logic (comparing a company against industry benchmarks) yet has zero test coverage.

```python
def test_gap_positive_when_ahead(self):
    company = self._make_report(domain_scores={"market": 4.0})
    bench   = self._make_report(domain_scores={"market": 3.0})
    gaps = company.score_gap_vs_benchmark(bench)
    assert gaps["market"] == pytest.approx(1.0)

def test_gap_negative_when_behind(self):
    ...

def test_gap_ignores_missing_domains(self):
    # domain present in company but not in benchmark should be absent from result
    ...
```

#### f) `DiagnosticReport.to_dict` — never tested (line 93)
Important for serialisation / API output. Should verify structure, rounded scores, and domain keys.

---

### 2. `src/data_processor.py` — 75% (16 lines missed)

#### a) `load_json` happy path (no test covers successful parse)
```python
def test_valid_json_returns_dict(self):
    result = load_json('{"domain": "market", "score": 3}')
    assert result == {"domain": "market", "score": 3}
```

#### b) `load_csv` — entirely untested (lines 20–21)
```python
def test_load_csv_parses_rows(self):
    raw = "domain,dimension,score\nmarket,user_research,3\n"
    rows = load_csv(raw)
    assert len(rows) == 1
    assert rows[0]["score"] == "3"
```

#### c) `validate_survey_row` — valid row and custom fields untested (line 47)
```python
def test_valid_row_returns_no_errors(self):
    assert validate_survey_row({"domain": "x", "dimension": "y", "score": "3"}) == []

def test_custom_required_fields(self):
    errors = validate_survey_row({"name": "Alice"}, required_fields=["name", "role"])
    assert any("role" in e for e in errors)
```

#### d) `normalise_score` edge cases (lines 49, 61, 64)
```python
def test_src_min_equals_src_max_raises(self):
    with pytest.raises(ValueError):
        normalise_score(3.0, src_min=3.0, src_max=3.0)

def test_out_of_range_raises(self):
    with pytest.raises(ValueError):
        normalise_score(101.0, src_min=0.0, src_max=100.0)
```

#### e) `detect_outliers` edge cases (lines 72, 83–91)
```python
def test_single_score_returns_empty(self):
    assert detect_outliers([3.0]) == []

def test_all_identical_scores_returns_empty(self):
    assert detect_outliers([3.0, 3.0, 3.0]) == []
```

#### f) `merge_survey_batches` — entirely untested (lines 83–91)
Deduplication logic is untested. Should cover: empty batches, single batch, duplicate keys across batches.

---

### 3. `src/report_generator.py` — 69% (13 lines missed)

This module has the lowest coverage and is the most user-facing — it directly controls what stakeholders see.

#### a) `render_text_report` — "Priority Improvement Areas" section (lines 41–44)
The conditional block that prints weak domains is never triggered in tests.

```python
def test_priority_section_appears_when_domain_below_threshold(self):
    report = _make_report(domain_scores={"weak": 2.0, "strong": 4.0})
    output = render_text_report(report)
    assert "Priority Improvement Areas" in output
    assert "weak" in output

def test_priority_section_absent_when_all_above_threshold(self):
    report = _make_report(domain_scores={"a": 3.5, "b": 4.0})
    output = render_text_report(report)
    assert "Priority Improvement Areas" not in output
```

#### b) `render_comparison_report` — entirely untested (lines 50–56)
```python
def test_comparison_shows_gaps(self):
    company   = _make_report("ACME",  domain_scores={"market": 4.0})
    benchmark = _make_report("Bench", domain_scores={"market": 3.0})
    output = render_comparison_report(company, benchmark)
    assert "ACME" in output
    assert "+1.00" in output
```

#### c) `render_json_report` — entirely untested (lines 60–61)
```python
def test_render_json_is_valid_json(self):
    import json
    report = _make_report(domain_scores={"a": 3.0})
    parsed = json.loads(render_json_report(report))
    assert parsed["company"] == "ACME"
    assert "overall_score" in parsed
```

#### d) `_score_bar` private helper (line ~30)
While private, the bar string is user-visible output. Test it indirectly through `domain_summary_line` with extreme scores (1 and 5).

---

## Recommended Prioritisation

| Priority | Area | Reason |
|---|---|---|
| **High** | `score_gap_vs_benchmark` | Core analytical feature with 0% coverage |
| **High** | `render_comparison_report` | User-facing benchmark output, 0% coverage |
| **High** | `render_json_report` | Serialisation output used downstream, 0% coverage |
| **High** | `merge_survey_batches` | Data deduplication logic, 0% coverage |
| **Medium** | `load_csv` | Input parsing, 0% coverage |
| **Medium** | `SubDimension` boundary validation | Prevents silent data corruption |
| **Medium** | `maturity_label` all levels | Parametrised test, low effort, high value |
| **Low** | `render_text_report` priority section | Important but UI-only |
| **Low** | `detect_outliers` edge cases | Defensive, rarely triggered |

## Target

Adding the tests listed above would raise total coverage from **75% → ~95%** and eliminate all zero-coverage functions.
