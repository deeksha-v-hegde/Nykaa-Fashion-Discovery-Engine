# 🛍️ Nykaa Fashion AI Discovery Engine

> **Evidence-Grounded Research Intelligence System for 30-Day Wishlist Reconsideration & Purchase Conversion**  
> *Built for Growth Product Managers to convert un-purchased wishlists into actionable, prioritised research opportunities.*

---

## 📌 Executive Summary & Problem Statement

Nykaa Fashion users frequently add apparel and beauty items to their wishlists, but a significant portion remain un-purchased after 30 days. Traditional e-commerce analytics reveal *that* conversion drops, but fail to explain *why* users hesitate.

The **Nykaa Fashion AI Discovery Engine** ingests, cleans, vectorizes, extracts, and quantifies real public user conversations (Google Play Store reviews, Apple App Store reviews, Reddit r/IndianFashionAddicts, and r/TwoXIndia) to surface **evidence-grounded purchase barriers, quantified themes ($N=1,151$), and ranked research opportunities**.

---

## 🏗️ System Architecture & Phase Breakdown

```text
                                [RAW UGC CORPUS]
                     (Google Play, App Store, Reddit, Forums)
                                       │
                                       ▼
  Phase 1 ──► Ingestion & Web Scraping (3,030 raw documents)
                                       │
  Phase 2 ──► Hinglish Normalization, Cleaning & Relevance Filter (1,158 relevant)
                                       │
  Phase 3 ──► Sublinear TF-IDF + Latent Semantic Analysis (384-dim vectors, 2,138 chunks)
                                       │
  Phase 4 ──► Grounded RAG Ask Engine (Verbatim citations, Non-monetary refusal)
                                       │
  Phase 5 ──► Structured Attribute Extraction (13-barrier taxonomy, 9 wishlist behaviours)
                                       │
  Phase 6 ──► Denominator-Bearing Quantification (N=1,151 canonical relevant sample)
                                       │
  Phase 7 ──► 6-Factor Prioritisation Scoring & Metric Journey Hops
                                       │
  Phase 8 ──► PM Dashboard Intelligence Services (Sections B through G)
                                       │
  Phase 9 ──► Ask Engine UI (10 One-Click Presets & 9 Response Sections)
                                       │
  Phase 10 ──► Weekly Monday Incremental Pipeline & Conflict Resolver (.github/workflows)
                                       │
  Phase 11 ──► Production Hardening, Chaos Testing & Streamlit UI (phase11/app.py)
```

---

## 🎯 Prioritised Research Shortlist ($N=1,151$)

The engine generates a transparently scored, evidence-grounded research shortlist for PMs:

$$\text{PrioritisationScore} = (0.20 \times \text{Freq}) + (0.25 \times \text{MetricRel}) + (0.20 \times \text{Pain}) + (0.15 \times \text{Evid}) + (0.10 \times \text{Cross}) + (0.10 \times \text{Solv})$$

| Rank | Opportunity Title | 6-Factor Score | Status | Primary Non-Monetary Intervention Strategy |
|---|---|---|---|---|
| **#1** | **Unpredictable Delivery SLAs and Post-Shipment Return Pickup Friction** | **4.84 / 5.0** | `validate_next` | Real-Time Delivery SLA Predictability & Self-Service Return Automation |
| **#2** | **Ethnic Wear Fit Uncertainty & Inconsistent Brand Size Charts (Likha, Gajra Gang)** | **4.64 / 5.0** | `under_investigation` | Standardized Garment Fit Predictor & Brand Size Chart Normalization |
| **#3** | **Fabric Material Discrepancies & Material Transparency Concerns** | **4.57 / 5.0** | `under_investigation` | Fabric Composition & Close-Up Material Transparency Gallery |
| **#4** | **Product Appearance vs Listing Studio Lighting Discrepancies** | **4.19 / 5.0** | `under_investigation` | Unedited Natural Light Photo Gallery & User Outfit Submissions |
| **#5** | **Styling & Complete Outfit Context Gap for Tops and Ethnic Wear** | **3.90 / 5.0** | `under_investigation` | Outfit Pairing Suggestions & Occasion Styling Context Cards |
| **#6** | **Wishlist Paralysis & Reconsideration Choice Overload** | **3.65 / 5.0** | `under_investigation` | Customizable Wishlist Folders & Side-by-Side Item Comparison Tool |

* **Rank 1 Label Rule**: Rank 1 is strictly labeled `"Recommended opportunity to validate"`. The system **never** claims a "Final Problem" or "Proven Root Cause".
* **30-Day Conversion Gap**: Hop 5 (`purchase_completion_30day`) is strictly marked **`UNKNOWN`** across all cards due to lack of longitudinal user tracking in public UGC.

---

## 🚀 Getting Started & Quick Start

### 1. Prerequisites & Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/nykaa/nykaa-fashion-discovery-engine.git
cd nykaa-fashion-discovery-engine
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:
```ini
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_STRATEGY=hybrid
RETRIEVAL_TOP_K=5
PORT=8000
HOST=0.0.0.0
```

### 2. Launch the Streamlit Web Application
Launch the PM Research Intelligence UI:
```bash
streamlit run phase11/app.py
```

### 3. Run Pipeline Verification Suite
Execute phase-by-phase verification:
```bash
# Execute Phase 11 hardening & chaos test
python -m phase11.run_phase11

# Execute Phase 10 weekly Monday pipeline
python -m phase10.run_phase10
```

---

## ⚙️ Key Architectural Guardrails & Enforcements

1. **Strict Denominator Control ($N=1,151$)**: All percentage statistics state `"X% of relevant analysed documents (N=1,151)"`. Claims such as *"X% of Nykaa users"* are strictly forbidden.
2. **Non-Monetary Interventions ONLY**: Queries regarding discounts, promo codes, or cashbacks are intercepted before retrieval with a standard refusal string (`MonetaryDetector`).
3. **Citation Provenance Integrity**: Every claim maps end-to-end:  
   $$\text{Answer} \longrightarrow \text{Citation} \longrightarrow \text{chunk\_id} \longrightarrow \text{document\_id} \longrightarrow \text{Source} \longrightarrow \text{URL} \longrightarrow \text{Verbatim Text}$$
4. **Source Isolation**: Nykaa internal review data (2,007 docs) vs broader fashion community sentiment (1,023 docs) are clearly separated with explicit disclaimer banners.
5. **Conflict Resolution**: When evidence disagrees (e.g. Garment sizing), both viewpoints are presented with the disclaimer *"Conflicting evidence detected. Additional primary research is required."*

---

## 📊 Source Status Registers Accounting (X / Y Sources)

| Source ID | Source Name | Scope | Status | Notes |
|---|---|---|---|---|
| `src_google_play_nykaa` | Google Play Store Reviews | Nykaa | **ACTIVE** | 741 relevant documents |
| `src_reddit_indianfashionaddicts` | Reddit r/IndianFashionAddicts | Broader | **ACTIVE** | 213 relevant documents |
| `src_reddit_twoxindia` | Reddit r/TwoXIndia | Broader | **ACTIVE** | 201 relevant documents |
| `src_apple_appstore_nykaa` | Apple App Store Reviews | Nykaa | **PARTIAL** | Public API rate-limited; pending official RSS sync |
| `src_youtube_fashion_reviews` | YouTube Try-On Hauls | Broader | **MANUAL_UNAVAILABLE** | Video transcript upload required |
| `src_x_twitter_nykaa_mentions` | X / Twitter Public Mentions | Nykaa | **MANUAL_UNAVAILABLE** | Paid API tier required |
| `src_fashion_community_forums` | Indian Fashion Web Forums | Broader | **MANUAL_UNAVAILABLE** | Scraping restricted by robots.txt |

---

## 🛡️ License & Portfolio Disclosure

Developed as a demonstration of **AI Product Management & Agentic Grounded RAG Architecture** for Nykaa Fashion. All evidence passages are drawn from public reviews and open online discussions.
