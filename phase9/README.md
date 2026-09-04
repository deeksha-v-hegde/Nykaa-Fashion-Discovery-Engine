# Phase 9 — Ask the Discovery Engine (Dedicated Page)

## Objective
Primary conversational research interface for product managers built on top of the Phase 4 `AskEngine`, integrating Phase 7 related research opportunities and Phase 8 citation inspection.

---

## Architectural Components

```text
phase9/
├── __init__.py             # Package exports
├── models.py               # Pydantic data contracts (PresetQuestionItem, GroundedAskSectionPayload, AskSessionState)
├── presets_catalogue.py    # 10 official research presets & 8 follow-up chips with real evidence badges
├── ask_session_service.py   # Multi-turn session manager & 9-section structured response generator
├── routes_ask_v2.py        # FastAPI routes for presets, query, and follow-ups (/api/ask/...)
├── run_phase9.py           # Standalone CLI runner and Ask Engine test suite
└── README.md               # Technical specification
```

---

## The 10 Official One-Click Research Presets

1. **Why do users add fashion products to their wishlist?** *(Strong Evidence N=1,151)*
2. **What prevents wishlisted products from being purchased?** *(Strong Evidence N=1,151)*
3. **What uncertainties remain after users have identified a product they like?** *(Strong Evidence N=1,151)*
4. **What causes users to postpone a purchase?** *(Strong Evidence N=1,151)*
5. **How do users compare multiple shortlisted products?** *(Moderate Evidence N=1,151)*
6. **What information do users seek outside Nykaa Fashion before purchasing?** *(Strong Evidence N=1,151)*
7. **What role do fit, size, styling, price, reviews, occasion, and social validation play?** *(Strong Evidence N=1,151)*
8. **When do users use the wishlist as genuine purchase intent versus a bookmark?** *(Moderate Evidence N=1,151)*
9. **How do these behaviours differ across user segments?** *(Moderate Evidence N=1,151)*
10. **What unmet needs emerge consistently across user conversations?** *(Strong Evidence N=1,151)*

---

## The 9 Rendered Response Sections

1. **Grounded Answer** (Verbatim/synthesized grounded copy)
2. **Evidence Passages** (Citations linked to raw text and URL)
3. **Pattern Summary** (Quantified corpus counts $N=1,151$)
4. **Inference Narrative**
5. **Confidence Rating & Rationale** (High / Medium / Low)
6. **Evidence Gap** (Discloses missing longitudinal user data)
7. **Metric Connection** (Wishlist $\rightarrow$ Reconsideration $\rightarrow$ Cart $\rightarrow$ 30-day UNKNOWN)
8. **Related Opportunities** (Linked Phase 7 cards)
9. **Suggested Follow-up Chips** (8 interactive follow-up actions)

---

## Execution
Run the Phase 9 verification test suite:
```bash
python -m phase9.run_phase9
```
