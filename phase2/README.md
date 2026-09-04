# Phase 2 — Cleaning, Deduplication, Relevance Classification & Chunking

## Objective
Transforms raw ingested documents from Phase 1 into unique, domain-relevant, chunked text suitable for Phase 3 vector embeddings and retrieval.

---

## Architectural Components

```text
phase2/
├── __init__.py           # Package exports
├── normalizer.py         # Unicode, whitespace, HTML entity, and boilerplate cleaning while preserving Hinglish and sizing
├── deduper.py            # Exact and near-duplicate shingling (marking duplicate_of audit trail)
├── classifier.py         # Domain relevance classifier for 30-day wishlist discovery barriers
├── chunker.py            # Sentence-boundary aware sliding window chunker
├── store.py              # SQLite repository for cleaning_logs, chunks, and document extensions
├── pipeline.py           # Master end-to-end Phase 2 orchestrator
├── run_phase2.py         # CLI runner and verification test suite
└── README.md             # This specification document
```

---

## Data Contracts

### 1. Document Extensions (`documents` table)
- `cleaned_text` (TEXT): Normalized text stripped of boilerplate.
- `relevance` (TEXT): `'relevant'` | `'not_relevant'` | `'unknown'`
- `relevance_reason` (TEXT): Audit trail of why document was accepted/rejected/flagged.
- `duplicate_of` (TEXT): Pointer to canonical document if near-duplicate.
- `cleaned_at` (TEXT): ISO-8601 UTC timestamp of cleaning run.

### 2. Chunk (`chunks` table)
- `chunk_id` (TEXT PRIMARY KEY): Format `chk_{document_id}_{ordinal}`
- `document_id` (TEXT FOREIGN KEY): Parent document ID
- `ordinal` (INTEGER): Zero-indexed chunk position
- `text` (TEXT): Chunk content
- `token_count` (INTEGER): Approximate token count
- `source_scope` (TEXT): `'nykaa'` | `'broader_fashion'`
- `source_id` (TEXT): Source registry identifier
- `embedding_version` (TEXT): Null until Phase 3 vector indexing
- `created_at` (TEXT): ISO-8601 UTC timestamp

---

## Execution
Run the Phase 2 pipeline independently:
```bash
python -m phase2.run_phase2
```
