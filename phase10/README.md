# Phase 10 — Conflicts, Coverage Ops & Weekly Incremental Pipeline

## Objective
Establishes the Nykaa Fashion Discovery Engine as an ongoing, automated research intelligence system with weekly Monday incremental pipelines, honest source status registers, and conflict presentation.

---

## Architectural Components

```text
phase10/
├── __init__.py               # Package exports
├── models.py                 # Structured Pydantic contracts (WeeklyRunRecord, SourceStatusItem, ConflictResult)
├── store.py                  # SQLite repository for weekly_runs and source_registers tables
├── source_registry.py        # Status connector registry for active and manual/unavailable sources
├── conflict_resolver.py      # Divergent viewpoint detector and conflict presentation engine
├── weekly_pipeline.py        # Master Monday incremental research pass orchestrator
├── routes_weekly.py          # FastAPI routes for weekly run status and trigger (/api/weekly/...)
├── run_phase10.py            # Standalone CLI runner and verification test suite
└── README.md                 # Technical specification
```

---

## Weekly Monday Ingestion Loop & Automated Flow

```text
GitHub Actions (.github/workflows/weekly_pipeline.yml)
      ↓
Source collectors (Phase 1)
      ↓
Hash/ID Gate (Skip processed document IDs/hashes)
      ↓
Data cleaning & deduplication (Phase 2)
      ↓
Relevance classification (Phase 2)
      ↓
Structured evidence extraction (Phase 5)
      ↓
Embeddings / Vector Index Upsert (Phase 3 — new chunks ONLY!)
      ↓
Theme Recount (Phase 6)
      ↓
Re-run Opportunity Prioritisation & Ranking (Phase 7)
      ↓
Dashboard Snapshot & Evolution Diff (Phase 8)
      ↓
Persist WeeklyRun Record to SQLite (data/discovery_engine.db)
```

---

## Conflict Presentation Rules

* When retrieved evidence contains opposing viewpoints (e.g. *Fit runs small* vs *Fit runs loose*), the system:
  1. Surfaces **`conflict_detected = True`**.
  2. Displays **`viewpoint_a`** and **`viewpoint_b`**.
  3. Displays explicit disclaimer: *"Conflicting evidence detected. Additional primary research is required to resolve conflicting user experiences."*
* **Forbidden**: Synthesizing a false consensus when public evidence disagrees!

---

## Execution
Run the Phase 10 weekly system test suite:
```bash
python -m phase10.run_phase10
```
