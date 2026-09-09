# 🛍️ Nykaa Fashion AI Discovery Engine

The **Nykaa Fashion AI Discovery Engine** is an evidence-grounded research and discovery platform that analyses public user conversations to identify unaddressed purchase barriers and prioritised research opportunities for Nykaa Fashion. Built for Product Managers, it bridges the gap between high-intent wishlist additions and 30-day purchase conversion.

---

## 🚀 Live Demo

Experience the interactive PM Research Intelligence Dashboard:  
👉 **[Nykaa Fashion AI Discovery Engine · Streamlit](https://nykaa-fashion-discovery-engine.streamlit.app/)**

---

## 📌 Problem

Fashion e-commerce shoppers frequently add apparel and beauty items to their wishlists—signaling high purchase intent—yet a substantial portion of wishlists remain unpurchased after 30 days.

Standard funnel analytics highlight *where* conversion drops off, but they cannot explain *why* users hesitate. Traditional user research methods, while qualitative, are often slow, ad-hoc, and disconnected from continuous market feedback.

This project ingests and structures public user-generated content (UGC) to surface evidence-grounded purchase barriers, map user hesitation patterns, and deliver systematically prioritised research opportunities for product and growth teams.

---

## 🔎 What the Engine Does

* **Public UGC Ingestion**: Collects unstructured reviews and open discussions from the Google Play Store, Apple App Store, and Reddit fashion communities.
* **Cleaning & Hinglish Normalization**: Filters noise, deduplicates text, and standardizes Hinglish expressions into an analysed canonical corpus ($N=1,151$).
* **Semantic & Vector Analysis**: Generates embeddings via TF-IDF and Latent Semantic Analysis (LSA) for deterministic similarity retrieval.
* **Grounded RAG / Ask Engine**: Delivers LLM-powered synthesis (via Groq Llama 3.3 70B) strictly constrained to verbatim retrieved evidence with source citations.
* **Structured Barrier & Behaviour Extraction**: Categorizes user friction into a 13-barrier taxonomy and maps 9 distinct wishlist behaviours.
* **Denominator-Controlled Quantification**: Computes barrier frequency against a fixed sample size ($N=1,151$) to eliminate ungrounded statistical claims.
* **6-Factor Opportunity Prioritisation**: Automatically ranks research opportunity areas across frequency, metric relevance, pain severity, evidence density, cross-source breadth, and solvability.
* **PM-Facing Streamlit Dashboard**: Presents interactive research shortlists, journey drop-off maps, verbatim evidence inspectors, and one-click discovery queries.

---

## 🏗️ High-Level Architecture

The platform processes qualitative voice-of-customer data through an end-to-end analytical pipeline:

```text
Public UGC (App Stores, Reddit)
             ↓
    Ingestion & Cleaning
             ↓
    Relevance Filtering
             ↓
  Semantic Retrieval / RAG
             ↓
Barrier & Behaviour Extraction
             ↓
       Quantification
             ↓
  Opportunity Prioritisation
             ↓
  PM Intelligence Dashboard
```

*(The underlying repository features a modular multi-phase architecture covering ingestion, vectorization, RAG synthesis, quantification, automated weekly pipelines, and UI hardening.)*

---

## 🎯 Key Research Output

The engine evaluates and ranks research opportunity areas using a transparent 6-factor framework:

$$\text{Prioritisation Score} = 0.20(\text{Freq}) + 0.25(\text{MetricRel}) + 0.20(\text{Pain}) + 0.15(\text{Evid}) + 0.10(\text{Cross}) + 0.10(\text{Solv})$$

| Rank | Opportunity | Score | Status | Non-Monetary Intervention Strategy |
|:---:|---|:---:|:---:|---|
| **#1** | **Unpredictable Delivery SLAs and Post-Shipment Return Pickup Friction** | **4.84 / 5.0** | `validate_next` | Real-Time Delivery SLA Predictability & Self-Service Return Automation |
| **#2** | **Ethnic Wear Fit Uncertainty & Inconsistent Brand Size Charts (Likha, Gajra Gang)** | **4.64 / 5.0** | `under_investigation` | Standardized Garment Fit Predictor & Brand Size Chart Normalization |
| **#3** | **Fabric Material Discrepancies & Material Transparency Concerns** | **4.57 / 5.0** | `under_investigation` | Fabric Composition & Close-Up Material Transparency Gallery |
| **#4** | **Product Appearance vs Listing Studio Lighting Discrepancies** | **4.19 / 5.0** | `under_investigation` | Unedited Natural Light Photo Gallery & User Outfit Submissions |
| **#5** | **Styling & Complete Outfit Context Gap for Tops and Ethnic Wear** | **3.90 / 5.0** | `under_investigation` | Outfit Pairing Suggestions & Occasion Styling Context Cards |
| **#6** | **Wishlist Paralysis & Reconsideration Choice Overload** | **3.65 / 5.0** | `under_investigation` | Customizable Wishlist Folders & Side-by-Side Item Comparison Tool |

> [!IMPORTANT]
> * **Validation Recommendation vs. Final Root Cause**: Rank #1 is strictly labeled as a **recommended opportunity to validate** via user interviews, not an assumed final problem or proven root cause.
> * **Metric Caveat**: The 30-day purchase-completion metric is designated **`UNKNOWN`** across all opportunity cards because public UGC does not support longitudinal user tracking.

---

## 📊 Evidence & Sources

| Source | Scope | Status | Relevant Documents |
|---|---|---|:---:|
| **Google Play Store Reviews** | Nykaa | Active | 741 |
| **Reddit r/IndianFashionAddicts** | Broader | Active | 213 |
| **Reddit r/TwoXIndia** | Broader | Active | 201 |
| **Apple App Store Reviews** | Nykaa | Partial | Public API rate-limited |
| **YouTube Try-On Hauls** | Broader | Unavailable | — |
| **X / Twitter Public Mentions** | Nykaa | Unavailable | — |
| **Indian Fashion Web Forums** | Broader | Unavailable | — |

---

## 🛡️ Research Guardrails

* **Denominator Control ($N=1,151$)**: All metrics cite exact sample denominators (e.g., *"X% of analysed relevant documents (N=1,151)"*), preventing unsupported generalizations like *"X% of all Nykaa users"*.
* **Evidence & Citation Provenance**: Every AI synthesis maps end-to-end to specific chunk IDs, source URLs, and verbatim user review excerpts.
* **Nykaa vs. Community Source Separation**: Nykaa internal app reviews (2,007 total docs) and broader fashion community sentiment (1,023 total docs) are strictly distinguished with explicit context banners.
* **Conflict Handling & Primary Research Mandate**: Discrepant findings trigger an explicit warning (*"Conflicting evidence detected. Additional primary research is required"*).
* **Non-Monetary Intervention Constraint**: Queries or interventions proposing discounts, promo codes, or cashback are programmatically intercepted to maintain focus on product and UX levers.

---

## 🛠️ Tech Stack

* **Web Application**: Streamlit
* **Language & Runtime**: Python 3.11+
* **LLM Inference**: Groq API (`llama-3.3-70b-versatile`)
* **Information Retrieval**: Scikit-Learn (Sublinear TF-IDF, TruncatedSVD / LSA), NumPy
* **Storage & Indexing**: SQLite (`discovery_engine.db`), Joblib
* **Data Scraping & Ingestion**: HTTPX, Google Play Scraper
* **Data Contracts & Schemas**: Pydantic v2, Pydantic-Settings

---

## ▶️ Run Locally

### 1. Clone and Install

```bash
git clone https://github.com/deeksha-v-hegde/Nykaa-Fashion-Discovery-Engine.git
cd Nykaa-Fashion-Discovery-Engine
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Deterministic vector retrieval operates offline without external API keys. To enable live Groq LLM synthesis:

```bash
cp .env.example .env
# Add your GROQ_API_KEY in .env
```

### 3. Launch Streamlit Application

```bash
streamlit run phase11/app.py
```

---

## 📄 License

Developed as a portfolio demonstration of evidence-grounded AI product discovery for Nykaa Fashion. All evidence passages are drawn from publicly available reviews and open community discussions.
