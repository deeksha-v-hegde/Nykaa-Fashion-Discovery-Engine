# Phase 8 — Dashboard Intelligence & Citation Inspector

## Objective
Provides PM-style research intelligence APIs and dashboard services for corpus overview, executive summary, opportunity board, platform comparison, segments, evidence explorer, and citation inspection.

---

## Architectural Components

```text
phase8/
├── __init__.py               # Package exports
├── models.py                 # Structured Pydantic contracts for Sections B-G
├── citation_inspector.py     # End-to-end citation provenance resolver (chunk -> doc -> URL)
├── dashboard_service.py      # Master dashboard aggregator for Sections B-G
├── routes_dashboard.py       # FastAPI dashboard routes (/api/dashboard/...)
├── run_phase8.py             # Standalone CLI runner and Evaluator Walk test suite
└── README.md                 # Technical specification
```

---

## Registered Dashboard API Endpoints

* **`GET /api/dashboard/overview`**: Sections B & C (Corpus Overview, Executive Summary, Coverage Gaps, Evolution Strip).
* **`GET /api/dashboard/board`**: Section D (Opportunity Board cards from Phase 7).
* **`GET /api/dashboard/comparison`**: Section E (Source & Platform Comparison with third-party disclaimer).
* **`GET /api/dashboard/segments`**: Section F (Segment Panel with low-sample $N<20$ warnings).
* **`GET /api/dashboard/explorer`**: Section G (Evidence Explorer for raw chunk browsing).
* **`GET /api/dashboard/citations/{chunk_id}`**: Citation Inspector resolving chunk ID to full provenance.

---

## Execution
Run the Phase 8 Evaluator Walk test suite:
```bash
python -m phase8.run_phase8
```
