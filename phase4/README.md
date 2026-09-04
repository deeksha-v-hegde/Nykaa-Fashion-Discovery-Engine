# Phase 4 — Grounded RAG Discovery Engine (Ask API)

## Objective
The core intelligence layer for Nykaa Fashion Product Managers. Provides a structured, cited discovery engine that synthesizes user purchase barriers from retrieved evidence chunks while strictly enforcing domain guardrails (monetary refusal, 30-day conversion uncertainty, citation validation, and source transparency).

---

## Architectural Components

```text
phase4/
├── __init__.py               # Package exports
├── models.py                 # Structured Pydantic contracts (DiscoveryResponse, EvidenceItem, MetricConnection)
├── monetary_detector.py      # Non-monetary guardrail intercepting discount/coupon queries before retrieval
├── query_processor.py        # Query normalization and sanitization
├── grounding_validator.py    # Citation validator ensuring quotes exist verbatim in retrieved chunks
├── confidence_scorer.py      # Multi-factor confidence rating (High/Medium/Low)
├── store.py                  # SQLite query trace repository (`query_traces` table)
├── ask_engine.py             # Master Grounded RAG discovery orchestrator
├── run_phase4.py             # Standalone CLI runner and verification test suite
└── README.md                 # Technical specification
```

---

## Data Contract: `DiscoveryResponse`

```json
{
  "query": "Why do shoppers hesitate to buy items saved in their wishlist?",
  "grounded_answer": "...",
  "evidence": [
    {
      "chunk_id": "chk_doc_6d6b2e4aa9e2_0",
      "document_id": "doc_6d6b2e4aa9e2",
      "snippet": "...",
      "source_id": "src_appstore_nykaa",
      "source_name": "Apple App Store Reviews",
      "platform": "Apple App Store",
      "source_type": "app_reviews",
      "source_scope": "nykaa",
      "published_at": "2026-02-19T20:12:00Z",
      "url": "https://...",
      "retrieval_relevance": 0.5419
    }
  ],
  "pattern": "Core observed user friction pattern.",
  "inference": "Inferred reason why this barrier causes hesitation.",
  "confidence": "High",
  "confidence_reason": "Strong semantic retrieval score across multiple platforms.",
  "evidence_gap": "What primary research or user interviews are still needed.",
  "metric_connection": {
    "wishlist_to_reconsideration": "observed",
    "reconsideration_to_confidence": "inferred",
    "confidence_to_cart": "inferred",
    "cart_to_purchase": "inferred",
    "thirty_day_conversion": "unknown",
    "explanation": "..."
  },
  "related_opportunity_ids": [],
  "nykaa_evidence_limited": false,
  "disclaimer_text": null,
  "conflict": null,
  "status": "success",
  "trace_id": "trace_..."
}
```

---

## Execution
Run the Phase 4 test runner:
```bash
python -m phase4.run_phase4
```
