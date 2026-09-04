# Phase 5 — Structured Extraction

## Objective
Extracts structured taxonomy attributes, purchase barriers, wishlist usage behaviors, workarounds, and evidence strength ratings from each **relevant canonical document**.

---

## Architectural Components

```text
phase5/
├── __init__.py           # Package exports
├── taxonomy.py           # Taxonomy allow-lists (WISHLIST_BEHAVIOURS, PURCHASE_BARRIERS)
├── models.py             # Structured Pydantic extraction schema (DocumentExtraction)
├── store.py              # SQLite repository for document_extractions table
├── extractor.py          # Document extractor enforcing Null-If-Unsupported policy
├── pipeline.py           # Batch processing orchestrator for relevant canonical documents
├── run_phase5.py         # Standalone CLI runner and audit test suite
└── README.md             # Technical documentation
```

---

## Data Contract: `document_extractions` Table

- `document_id` (TEXT PRIMARY KEY): Foreign key to `documents`
- `product_category` (TEXT): Category of apparel or product (e.g., Ethnic Wear, Western, Footwear)
- `user_behaviour` (TEXT): Observed user shopping action
- `wishlist_behaviour` (TEXT): Taxonomy key (e.g. `bookmark_save_for_later`, `compare_alternatives`, `future_occasion`, `waiting_timing`)
- `barrier` (TEXT): Primary purchase barrier taxonomy key (`fit_size`, `quality`, `product_vs_image`, `styling`, `decision_paralysis`, `price_timing`, `availability`, `delivery_logistics`, `other_emerging`)
- `uncertainty` (TEXT): Specific doubt or hesitation detail
- `workaround` (TEXT): User compensating action
- `other_new_theme` (TEXT): Custom emerging theme string
- `evidence_strength` (TEXT): `'high'` | `'medium'` | `'low'`
- `extracted_at` (TEXT): ISO-8601 timestamp

---

## Execution
Run the Phase 5 extraction pipeline and audit suite:
```bash
python -m phase5.run_phase5
```
