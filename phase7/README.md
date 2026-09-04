# Phase 7 — Opportunities, Scoring & Metric Journey

## Objective
Turns extracted user friction patterns into a ranked, cited **research shortlist** for Nykaa Growth Product Managers.

---

## Architectural Components

```text
phase7/
├── __init__.py           # Package exports
├── models.py             # Structured Pydantic contracts (OpportunityCard, MetricJourneyHops, ScoringBreakdown)
├── store.py              # SQLite repository for opportunities and opportunity_snapshots tables
├── clusterer.py          # Opportunity candidate generator based on recurring barriers
├── evidence_picker.py    # Retrieves 3-5 verbatim chunk citations via Phase 3 retriever
├── scorer.py             # Transparent 6-factor prioritisation scorer (1.0-5.0 scale)
├── journey_builder.py    # Metric journey visualization builder (30-day hop strictly 'unknown')
├── pipeline.py           # Master Phase 7 pipeline orchestrator and ranker
├── run_phase7.py         # Standalone CLI runner and verification test suite
└── README.md             # Technical documentation
```

---

## 6-Factor Prioritisation Score Formula

$$\text{PrioritisationScore} = \sum_{i=1}^{6} (\text{Score}_i \times \text{Weight}_i)$$

* **Frequency** (Weight: 0.20): Scale of occurrences out of $N=1,151$.
* **Metric Relevance** (Weight: 0.25): Friction impact on wishlist consideration & cart transition.
* **User Pain** (Weight: 0.20): Frustration severity expressed in user text.
* **Evidence Strength** (Weight: 0.15): Proportion of `high` quality extractions.
* **Cross-Source Consistency** (Weight: 0.10): Presence across multiple source types (`app_reviews` & `community_discussion`).
* **Solvability** (Weight: 0.10): Feasibility of non-monetary product/AI feature intervention.

---

## Data Guardrails Enforced

1. **Rank 1 Label Rule (`DOM-03`)**: Rank 1 is strictly labeled `"Recommended opportunity to validate"` with status `validate_next`. Title never contains "Final Problem" or "Proven Root Cause".
2. **Non-Monetary Interventions ONLY (`DOM-01`)**: Interventions are non-monetary strategy types. Discounts, coupons, and cashbacks are excluded.
3. **30-Day Conversion Gap (`DOM-02`)**: Hop 5 (`purchase_completion_30day`) is strictly `unknown`.

---

## Execution
Run the Phase 7 opportunity pipeline and audit test suite:
```bash
python -m phase7.run_phase7
```
