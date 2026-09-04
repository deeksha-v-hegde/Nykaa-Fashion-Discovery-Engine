# Phase 1 — Ingestion

**System:** Nykaa Fashion — AI Wishlist Discovery Engine  
**Module:** `phase1/`  
**Purpose:** Bring publicly and legally accessible documents into the corpus store with deterministic SHA-256 hashes and provenance tags.

---

## 1. Directory Structure

```text
phase1/
├── base.py              # Collector abstract base class & DocumentDraft schema
├── store.py             # Phase 1 SQLite persistence & hash-gating repository
├── ingest.py            # Master IngestJob workflow coordinator
├── run_phase1.py        # Standalone verification runner script
├── README.md            # Phase 1 specification & documentation
└── adapters/
    ├── playstore.py     # Google Play Store reviews collector (nykaa)
    ├── appstore.py      # Apple App Store reviews collector (nykaa)
    ├── reddit.py        # Reddit r/IFA & r/TwoXIndia collector (broader_fashion)
    └── manual.py        # Manual/restricted sources adapter (0 fake rows)
```

---

## 2. Phase 1 Data Contract

Every ingested document adheres to the strict data contract:

| Field | Type | Description |
|---|---|---|
| `document_id` | `TEXT` (PK) | Unique identifier (`doc_<hex>`) |
| `source_id` | `TEXT` (FK) | Foreign key to registered Source |
| `url` | `TEXT` | Public permalink or platform ID |
| `published_at` | `TEXT` (ISO) | Original publication timestamp (nullable) |
| `raw_text` | `TEXT` | Raw user review or discussion text |
| `content_hash` | `TEXT` (Unique) | Deterministic SHA-256 hash of normalized text |
| `source_scope` | `TEXT` | `nykaa` or `broader_fashion` |
| `ingested_at` | `TEXT` (ISO) | UTC timestamp of ingestion |
| `run_id` | `TEXT` | Associated ingest run batch ID |

---

## 3. Exit Criteria Compliance

1. **Real Public Documents**: Automated adapters fetch authentic public reviews for Nykaa Fashion and peer discussions on Reddit.
2. **Honest Manual Sources**: Non-automatable or restricted platforms (YouTube, Twitter/X, Forums) are marked `manual_unavailable` with **zero fake rows**.
3. **Deterministic Deduplication**: Subsequent ingestion runs detect existing SHA-256 hashes and skip them (`skipped_duplicate`), never double-counting documents.
4. **Source Scopes**: Every document is strictly partitioned into `nykaa` or `broader_fashion`.

---

## 4. How to Run & Verify

Run the standalone Phase 1 runner:
```bash
python -m phase1.run_phase1
```
