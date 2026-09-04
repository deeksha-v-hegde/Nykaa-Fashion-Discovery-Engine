# Phase 6 — Quantification and Coverage/Gaps Catalogue

## Objective
Computes honest, denominator-bearing corpus statistics and catalogs structural data gaps for the Nykaa Fashion Discovery Engine.

---

## Architectural Components

```text
phase6/
├── __init__.py           # Package exports
├── models.py             # Structured Pydantic contracts (StatItem, QuantificationReport, CoverageGapItem)
├── store.py              # SQLite repository for quantification_snapshots and coverage_gaps tables
├── quantifier.py         # Denominator-bearing aggregator (N=1,151) enforcing strict percentage copy templates
├── coverage_gaps.py      # Structural gaps and corpus coverage calculator
├── run_phase6.py         # Standalone CLI runner and verification test suite
└── README.md             # Technical documentation
```

---

## Data Contracts & Enforced Copy Template

### 1. Mandatory Denominator Template
Every percentage output MUST be formatted as:
$$\text{"\textless Theme\textgreater\ appears in X\% of relevant analysed documents (N=1,151)."}$$

* **Allowed**: *"Fit uncertainty appears in 11.2% of relevant analysed documents (N=1,151)."*
* **Forbidden**: *"11.2% of Nykaa users have fit problems."*

---

## Execution
Run the Phase 6 quantification pass and verification test suite:
```bash
python -m phase6.run_phase6
```
