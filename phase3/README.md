# Phase 3 — Embeddings and Vector Index

## Objective
Indexes Phase 2 retrieval chunks into a persistent vector database with complete metadata filters, enabling fast semantic and hybrid retrieval for Phase 4 Grounded RAG.

---

## Architectural Components

```text
phase3/
├── __init__.py           # Package exports
├── embedder.py           # Dense 384-dim semantic embedder with LSA/SVD projection and L2-normalization
├── vector_store.py       # SQLite vector repository with BLOB storage, metadata indexing, and in-memory matrix cache
├── indexer.py            # Incremental batch indexer checking chunk embedding_version
├── retriever.py          # Vector and hybrid search engine with scope/source/date metadata filters
├── run_phase3.py         # Standalone CLI runner and verification suite
└── README.md             # Technical documentation
```

---

## Data Contracts

### 1. Vector Record (`chunk_vectors` table)
- `chunk_id` (TEXT PRIMARY KEY): Associated chunk ID (e.g. `chk_doc_9246c1b5d73a_0`)
- `document_id` (TEXT): Parent document ID
- `vector` (BLOB): Normalized 384-dimensional float32 vector
- `dim` (INTEGER): `384`
- `embedding_model` (TEXT): Model version string (e.g. `tfidf-lsa-384`)
- `source_scope` (TEXT): `'nykaa'` | `'broader_fashion'`
- `source_id` (TEXT): Source registry identifier (e.g. `src_playstore_nykaa`)
- `source_type` (TEXT): `'app_reviews'` | `'community_discussion'`
- `published_at` (TEXT): ISO-8601 UTC timestamp
- `token_count` (INTEGER): Chunk token count
- `indexed_at` (TEXT): Index timestamp

---

## Execution
Run the Phase 3 vector indexer and verification test suite:
```bash
python -m phase3.run_phase3
```
