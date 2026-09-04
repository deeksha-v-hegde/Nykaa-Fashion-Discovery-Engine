# Problem Statement

## Problem Statement: Nykaa Fashion — Evidence-Backed Product Discovery Engine

## Overview

This project is a RAG-based AI Discovery Engine.

**Product:** Nykaa Fashion  
**Business metric:** Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.

Users browse fashion products, save items they like, and add them to wishlists. A wishlist is a high-intent signal: explicit interest without a purchase. Wishlists often grow large while conversion stays low.

This system does **not** solve conversion yet. It uses public user-generated evidence to:

1. Understand wishlist-related behaviours
2. Identify barriers and uncertainties that may prevent purchase
3. Identify user segments where evidence exists
4. Quantify recurring themes where the corpus allows
5. Compare opportunity areas
6. Connect those areas to the 30-day wishlist-to-purchase metric
7. Generate hypotheses for 5–6 user interviews

The user problem is **not given**. The final problem and solution come only after primary research.

Do not build a generic chatbot. Build an **AI Product Discovery Engine**. Central question:

> What user problems may be preventing wishlisted fashion products from becoming purchases within 30 days?

Every insight follows:

**Evidence → Pattern → Inference → Opportunity → Metric connection → Research hypothesis**

Do not jump from a review to a solution.

## Objective

Design and implement a modular RAG discovery dashboard that:

- Analyses a curated public corpus about online fashion shopping and wishlists
- Distinguishes observed evidence, patterns, inferences, and hypotheses
- Identifies, quantifies, scores, and compares opportunity areas for 30-day wishlist conversion
- Produces a **research shortlist** for interviews — not a final problem or product solution
- Stays evidence-only, cited, and non-monetary (no discounts as a lever)
- Includes a dedicated **Ask the Discovery Engine** page
- Refreshes the corpus with an **incremental Monday-morning** research pipeline
- Uses **Groq** for fast grounded generation; retrieval (not the LLM’s general knowledge) supplies evidence

## Target Users

- Growth Product Managers investigating wishlist-to-purchase conversion

## Scope of Work

### 1. Corpus

Focus on **Nykaa Fashion**, plus comparable public fashion-shopping conversations when Nykaa-specific volume is limited.

Index public user-generated sources, including App Store and Play Store reviews, Reddit, fashion/shopping communities, social media, YouTube comments, product reviews and Q&A, and other public conversations about online fashion shopping.

Always distinguish **Nykaa-specific evidence** from **broader online fashion-shopping evidence**. If Nykaa-specific evidence is thin, say so:

> Nykaa-specific evidence is limited for this theme. The following pattern is supported primarily by broader online fashion-shopping conversations.

Never present third-party sources as Nykaa internal data.

### 2. Evidence discipline

| Layer | Meaning |
| --- | --- |
| **Observed evidence** | What users explicitly said in the indexed corpus |
| **Pattern** | A recurring theme across multiple pieces of evidence |
| **Inference** | What that may imply for wishlist → purchase |
| **Hypothesis** | A problem statement that needs primary research |

Never present inference or hypothesis as fact.

**Bad:** Users abandon wishlists because of fit uncertainty.  
**Good:** Multiple users in the corpus report fit and sizing uncertainty. This suggests fit confidence may be a purchase barrier, but the corpus does not show that these users abandoned wishlist items because of fit. Validate in interviews.

**Allowed chain (example):**

- **Evidence:** Users repeatedly mention uncertainty about sizing.
- **Pattern:** Fit and size uncertainty recur across sources.
- **Inference:** Users may lack confidence to buy fashion online.
- **Opportunity:** Improve purchase confidence around fit.
- **Research hypothesis:** High-intent wishlist users may postpone purchase when they cannot predict fit.

The engine may label a **Recommended opportunity to validate**. It must **not** declare a final problem, confirmed root cause, or proven reason for 30-day conversion failure.

Final problem definition: **Business metric → AI discovery → Primary research**.

Public reviews do **not** provide reliable user-level 30-day conversion data. Do not claim actual conversion rates, 30-day purchase rates, user-level wishlist behaviour unless the source states it, or causality between a complaint and wishlist abandonment.

If the corpus cannot answer:

> The indexed corpus does not provide sufficient evidence to answer this directly.

Then state what primary research or product data would be required. Do not invent an answer to fill the gap.

### 3. Structured extraction

For each relevant document, extract attributes **only where supported**: source, platform, source type, date, product/category, user behaviour, wishlist behaviour (if explicit), purchase intent and stage, barrier, uncertainty, user job, workaround, external information source, alternative considered, occasion, fit/size, styling, price, reviews/social validation, availability, quality/expectation, other/new theme, evidence strength.

Do not force a category. Allow **Other / emerging theme**.

**Wishlist behaviour taxonomy** (starting set, not exhaustive): genuine purchase intent, bookmark/save-for-later, compare alternatives, future occasion, waiting/timing, need more information, inspiration, price monitoring, other.

Do not treat every wishlist mention as purchase intent.

**Purchase barriers** (starting set): fit/size, quality, product-vs-image, styling, decision paralysis, price/timing, availability, social validation, reviews/information gaps, occasion/timing, trust, other emerging themes. The model must find new themes from the corpus.

### 4. Quantification

Where possible: mention count, share of relevant analysed documents, source / theme / segment distribution, cross-source consistency.

Every statistic must include a **denominator**.

**Allowed:** Fit uncertainty appears in 27% of relevant analysed documents (N=1,842).  
**Not allowed:** 27% of Nykaa users have fit problems.

These are **corpus-level** figures, not population claims, unless representative user-level data exists.

### 5. Opportunities

Turn recurring patterns into opportunity areas. Each opportunity includes:

- Problem name (one line)
- User job
- Blocker
- Evidence (3–5 strongest retrieved snippets)
- Scale (count and/or share of relevant corpus)
- Metric connection on **Wishlist → Reconsideration → Confidence → Cart → Purchase**, with each hop labelled **Observed / Inferred / Unknown**
- Current workaround
- Confidence (High / Medium / Low)
- Evidence gap
- Research hypothesis for 5–6 interviews
- Non-monetary intervention **type** only — no discounts, coupons, cashback, or price-drop campaigns; do not lock a product solution before research

**Scoring (1–5 each):** frequency, metric relevance, user pain / behavioural impact, evidence strength, cross-source consistency, AI/product solvability (non-monetary).

Use a **transparent weighted formula**. Show component scores. Label the result **Research prioritisation score** — not objective truth.

**Opportunity Board** (most prominent analytical section). Each card: name, user job, core blocker, mention count, share of relevant corpus, evidence confidence, metric relevance, workaround, score, sources, research hypothesis, “Validate next” status.

Rank by research priority. Highest card: **Recommended opportunity to validate** — never “Final problem”.

**Journey visualisation per opportunity:**

**Wishlist added → Reconsideration → [Barrier] → Purchase postponed / alternative action → No purchase within 30 days**

Label observed vs inferred vs unknown.

**Explore Evidence** opens supporting and related passages, source and theme distribution, segments, contradictory evidence, gaps, and related discovery questions.

Path: **Opportunity → Claim → Evidence → Source**

### 6. Dashboard

PM-style research intelligence tool — not a chatbot.

**Header**

- Title: **Nykaa Fashion — AI Wishlist Discovery Engine**
- Subtitle: Discovering user barriers to 30-day wishlist-to-purchase conversion
- Disclaimer: **Evidence-only discovery. No discounts. No unsourced claims.**

**Corpus overview:** documents indexed and relevant, source types, date coverage, theme and segment counts, Coverage & Gaps, weekly run status, corpus evolution (**Previous corpus → New evidence → Updated themes → Updated opportunities**).

**Executive discovery summary:** top wishlist behaviours, barriers, uncertainties, workarounds, important gaps.

**Opportunity Board** — primary analysis section.

**Source comparison** — filters: source, source type, time, theme, segment, intent.

**Segment analysis** — purchase intent, shopper type, occasion, category, or other evidence-backed segments. If thin: **Insufficient evidence for reliable segmentation.**

**Evidence explorer** — snippet, source, source type, date, URL, relevance score when available.

**Ask the Discovery Engine** — dedicated page (section 7).

**Citation inspector:** Claim → retrieved passages → source → date → URL. No evidence → no claim.

**Conflicts:** show **Conflicting evidence detected**, present both sides, do not force one narrative. If unresolved: **Additional primary research is required.**

**Weak retrieval:** **Insufficient evidence**, plus what the corpus contains, what is missing, and what research/data is needed.

**Discount queries** — refuse:

> Monetary incentives are outside the project scope. I can instead identify evidence-backed non-monetary barriers and opportunities that may influence wishlist-to-purchase conversion.

**UX:** hierarchy, evidence visibility, explainability, comparability, short answers, drill-down, fact vs inference. Avoid word clouds, generic sentiment charts, decorative AI, long essays, unsupported percentages, fake precision, unsupported personas.

**Build order** (do not overbuild): grounding → extraction → opportunities → quantification → scoring → metric connection → citation inspector → coverage/gaps → UX → polish. Ship something functional, explainable, and deployable.

### 7. Ask the Discovery Engine

Dedicated page. Primary conversational research UI.

Must include:

- Free-form question input and follow-ups
- Ten one-click discovery questions:
  1. Why do users add fashion products to their wishlist?
  2. What prevents wishlisted products from being purchased?
  3. What uncertainties remain after users have identified a product they like?
  4. What causes users to postpone a purchase?
  5. How do users compare multiple shortlisted products?
  6. What information do users seek outside Nykaa Fashion before purchasing?
  7. What role do fit, size, styling, price, reviews, occasion, and social validation play?
  8. When do users use the wishlist as genuine purchase intent versus a bookmark?
  9. How do these behaviours differ across user segments?
  10. What unmet needs emerge consistently across user conversations?
- Filters: source/platform, source type, time range, theme, user intent, segment (when supported)
- Drill from insight to evidence

Each predefined question shows evidence strength (strong / moderate / weak or insufficient) and a reason when relevant. Example:

> **30-day wishlist behaviour: Weak evidence.** Public conversations do not contain sufficient user-level behavioural data to establish whether a user purchased a wishlisted item within 30 days.

**Every answer uses visible sections** (not one generated paragraph):

1. Grounded answer — retrieved evidence only
2. Evidence — 3–5 strongest passages (snippet, platform, source type, date, URL, retrieval relevance)
3. Pattern
4. Inference (labelled, not fact)
5. Confidence (High / Medium / Low) from coverage, source diversity, retrieval quality, consistency
6. Evidence gap
7. Metric connection on **Wishlist → Reconsideration → Confidence → Cart → Purchase → 30-day conversion**, each hop Observed / Inferred / Unknown
8. Related opportunities

Evaluator path on this page:

**Question → Grounded Answer → Evidence → Pattern → Inference → Metric Connection → Potential Opportunity → Research Hypothesis → Interview Validation**

**Follow-up actions** (new RAG queries, same grounding rules): Show more evidence, Quantify this, Compare sources, Compare segments, Find contradictory evidence, Explain the pattern, What don’t we know?, What should I validate in interviews?

### 8. Weekly research pipeline

Every **Monday morning**, incrementally:

1. Collect newly available public reviews, discussions, comments, and supported sources
2. Keep only new / unprocessed content
3. Clean and normalise
4. Deduplicate
5. Classify relevance to wishlist-to-purchase discovery
6. Extract behavioural signals, barriers, uncertainties, jobs, workarounds
7. Embed and add relevant documents to the RAG index
8. Recalculate theme and opportunity counts
9. Re-run opportunity analysis and prioritisation
10. Update dashboard stats, insights, evidence, and Opportunity Board
11. Log status, timestamp, new documents, relevant documents, source failures

Do not reprocess the whole corpus by default. Persist last successful run, source-level status, processed document IDs/hashes, new and relevant counts, failed sources, processing errors, analysis timestamp.

**Overview must show:** last updated; next scheduled run; new documents this week; new relevant documents; sources successfully updated (X / Y); sources with errors; analysis status (Success / Partial / Failed).

Corpus evolution: **Previous corpus → New evidence → Updated themes → Updated opportunities**. This is an ongoing research system, not a one-off analysis.

Scheduler: **GitHub Actions** or equivalent:

```text
Monday morning → scheduled workflow → collectors → clean/dedupe
→ relevance → extraction → embeddings/index → opportunity analysis
→ dashboard update → corpus updated
```

Collect only content that is legally and technically accessible via the chosen method. Do not bypass authentication, paywalls, CAPTCHAs, access controls, robots rules, or platform protections.

If a source cannot be automated, mark it **Manual / unavailable for automated weekly collection**. Do not fabricate it or hide its status.

### 9. RAG technology stack

Modular pipeline:

**Data Sources → Ingestion → Cleaning → Chunking → Embeddings → Vector Database → Retrieval → LLM → Dashboard**

**Groq** is the LLM inference layer for: answer generation, evidence synthesis, pattern identification, evidence vs inference classification, structured extraction, opportunity analysis, follow-up questions.

The LLM receives **only retrieved context**. Retrieval finds evidence; Groq does not answer from general knowledge. Keep the LLM layer swappable without rebuilding the pipeline.

**Per question:**

```text
User Question → Query Processing → Vector / Hybrid Retrieval
→ Top Relevant Evidence → Groq LLM → Structured Discovery Response
→ Answer / Pattern / Inference / Evidence Gap / Metric Connection
   / Related Opportunities → Citation Inspector
```

**Dashboard and README** list: LLM provider (Groq), model, embedding model, vector database, retrieval strategy, chunking strategy, top-K. Models via **environment variables**, not hard-coded.

**If Groq is unavailable or rate-limited:** clear error state; no unsupported answer; keep access to indexed evidence; record the failed run; do not silently substitute ungrounded content.

## Constraints

### Data and sources

- Public corpus only; no invented quotes, URLs, statistics, users, or behaviours
- Nykaa-specific vs broader fashion evidence labelled
- No scraping behind auth, paywalls, CAPTCHAs, access controls, robots rules, or platform protections
- Non-automatable sources labelled **Manual / unavailable for automated weekly collection**

### Metric honesty

- No fake 30-day conversion rates or causal wishlist-abandonment claims
- Corpus percentages always include a denominator

### Solution

- Product: **Nykaa Fashion** only
- Metric: purchase of at least one wishlisted item **within 30 days** of add
- No monetary incentives
- Dashboard does not decide the “final problem”

### RAG / Groq

- Generate only from retrieved context
- Models configurable via env vars
- Groq outage: error + indexed evidence + logged failure; no ungrounded fallback

## Expected Deliverables

1. **Discovery dashboard** — header, corpus overview, executive summary, Opportunity Board, source comparison, segments, evidence explorer, citation inspector, conflicts, coverage & gaps, weekly run status, stack transparency, dedicated Ask page
2. **README** — setup, corpus, RAG architecture, scoring formula, limitations, weekly scheduler, incremental index, source status, Groq/model/embeddings/vector DB/retrieval/chunking/top-K, env-based config
3. **Disclaimer:** “Evidence-only discovery. No discounts. No unsourced claims.”

## Success Criteria

An evaluator can move:

**Raw public conversations → behaviours → barriers → patterns → quantified themes → opportunity comparison → highest-priority opportunity → evidence → metric connection → research hypothesis**

And on Ask:

**Question → Grounded Answer → Evidence → Pattern → Inference → Metric Connection → Opportunity → Research Hypothesis → Interview Validation**

Core question:

> Can a Growth PM use this dashboard to see which user problems are most worth investigating for 30-day wishlist-to-purchase conversion, with every important conclusion traceable to real evidence?

Also required: grounded answers only; evidence/inference/hypothesis labels; research prioritisation scores; discount and weak-evidence handling; Nykaa vs broader source labels; weekly incremental pipeline with Overview status; Groq modular stack with env-based models and a clear outage state.

## Summary

Build an explainable Product Discovery Engine for Nykaa Fashion wishlist conversion. Retrieval finds public evidence; Groq generates structured, cited insights. Rank opportunities as a research shortlist, connect each theme to the 30-day purchase journey, and refresh the corpus weekly. Do not ship discounts, unsourced claims, chatbot essays, or a “final problem” before interviews.
