# Phase-wise architecture

**System:** Nykaa Fashion — AI Wishlist Discovery Engine  
**Requirements:** [probemstatement.md](./probemstatement.md)  
**User:** Growth Product Manager investigating wishlist → purchase within 30 days of add.

This file is the **implementation architecture**, organised as sequential phases. Do not skip grounding (Phase 4) to decorate the UI (Phase 11). Do not declare a final product problem in any phase.

---

# How to read this document

| Section | Meaning |
| --- | --- |
| **Objective** | What this phase exists to produce |
| **Depends on** | Phases that must be done first |
| **Problem-statement mapping** | Which requirements this phase satisfies |
| **Inputs / outputs** | Data in and data out |
| **Components** | Modules to build |
| **Step-by-step** | Runtime or batch flow |
| **Data contract** | Fields that must exist |
| **Failure behaviour** | What happens when something breaks |
| **UI in this phase** | What the PM sees (if anything) |
| **Exit criteria** | When to start the next phase |
| **Out of scope** | What this phase must not do |

**Global pipeline (all phases together):**

```text
Data Sources → Ingestion → Cleaning → Chunking → Embeddings
→ Vector Database → Retrieval → Groq LLM → Dashboard
```

**Global Ask pipeline (Phases 4 and 9):**

```text
User Question → Query Processing → Vector / Hybrid Retrieval
→ Top Relevant Evidence → Groq LLM → Structured Discovery Response
→ Answer, Pattern, Inference, Evidence Gap, Metric Connection,
   Related Opportunities → Citation Inspector
```

**Global insight chain (never collapse into one paragraph):**

Evidence → Pattern → Inference → Opportunity → Metric connection → Research hypothesis

---

# Cross-cutting rules (apply in every phase)

1. Groq receives **retrieved or document-local text only**, never “answer from general knowledge”.
2. Model names, top-K, chunk size, embedding model, vector DB URL come from **environment variables**.
3. Every document is tagged `source_scope`: `nykaa` | `broader_fashion`. Broader-heavy answers must say Nykaa-specific evidence is limited.
4. Statistics are **corpus-level** and always include denominator N (relevant analysed documents). Never “X% of Nykaa users”.
5. No invented quotes, URLs, users, or conversion rates. No causal wishlist abandonment unless the source states it.
6. No discounts, coupons, cashback, or price-drop campaigns as solutions.
7. If Groq is down or rate-limited: **error UI**, keep indexed evidence, **log the failure**, do not invent an answer.
8. Legal collection only. No auth, paywall, CAPTCHA, robots, or platform-protection bypass. Otherwise mark source **Manual / unavailable for automated weekly collection**.
9. Top opportunity label: **Recommended opportunity to validate**. Never “Final problem”, “root cause confirmed”, or “proven 30-day conversion failure”.

---

# Target technical shape (end state after Phase 11)

```text
GitHub Actions (Monday morning)
        │
        ▼
Collectors → Corpus store → Clean/dedupe/relevance → Extract
        → Chunk/embed → Vector index → Opportunity analytics
        → WeeklyRun log → Dashboard snapshot

Growth PM ← Dashboard ← Discovery API
                           Retrieval + Groq + validators
```

**Stores**

- Relational or document DB: sources, documents, chunks (text + ids), extractions, opportunities, weekly runs, hashes, query traces.
- Vector DB: embeddings keyed by `chunk_id` with metadata filters.
- Shared IDs so **Opportunity → Claim → Evidence → Source** is a database join.

---

# Environment variables (Phase 0 onward)

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Inference |
| `GROQ_MODEL` | Chat model (swappable) |
| `EMBEDDING_MODEL` | Embedding model |
| `VECTOR_DB_URL` | Vector database |
| `RETRIEVAL_STRATEGY` | `vector` or `hybrid` |
| `RETRIEVAL_TOP_K` | Retrieval depth |
| `CHUNK_SIZE` | Chunk length |
| `CHUNK_OVERLAP` | Overlap |
| Score weights | Research prioritisation formula |

Dashboard Stack panel and README display these values at runtime. Do not hard-code model names in application source.

---

# Suggested modules (map onto phases)

```text
config/           Phase 0
pipeline/sources  Phase 1
pipeline/clean    Phase 2
pipeline/index    Phase 3
llm/              Phase 0, 4, 5, 7, 9
api/ask           Phase 4, 9
pipeline/extract  Phase 5
pipeline/stats    Phase 6
pipeline/opps     Phase 7
app/overview      Phase 8, 10
app/board         Phase 7, 8
app/ask           Phase 9
.github/workflows Phase 10
```

---

# Phase 0 — Foundation

### Objective

Create a runnable application skeleton, configuration, source register, and PM chrome so later phases plug in without rewriting the shell.

### Depends on

None.

### Problem-statement mapping

Header title/subtitle/disclaimer; modular LLM; env-based models; stack transparency placeholders; “do not overbuild”.

### Inputs

- Empty repo
- Problem statement constraints

### Outputs

- Bootable dashboard with header
- `.env.example`
- LLM provider **interface** + Groq adapter stub
- Source registry file or table (empty or seed rows)
- README stub

### Components

| Component | Role |
| --- | --- |
| Dashboard shell | Header, empty Overview, empty Ask route |
| `config` | Load env |
| `llm.Provider` | `generate(prompt, context_chunks) -> structured JSON` |
| `llm.GroqAdapter` | Implements Provider using Groq |
| `sources.yaml` or `Source` table | Name, platform, collection_mode, scope |

### Step-by-step

1. Create app + API entrypoints.
2. Render header:
   - Title: **Nykaa Fashion — AI Wishlist Discovery Engine**
   - Subtitle: Discovering user barriers to 30-day wishlist-to-purchase conversion
   - Disclaimer: **Evidence-only discovery. No discounts. No unsourced claims.**
3. Load Groq model name from env; fail startup if key missing in production, warn in local.
4. Seed source register with intended sources (App Store, Play Store, Reddit, communities, social, YouTube, reviews/Q&A). Set unknown automation to `manual_unavailable` until Phase 1 proves otherwise.
5. Stack panel shows “not configured” until env is set — never fake a model name.

### Data contract

**Source (seed)**

- `source_id`, `name`, `platform`, `source_type`
- `source_scope`: `nykaa` | `broader_fashion`
- `collection_mode`: `automated` | `manual_unavailable`

### Failure behaviour

Missing env: app still shows disclaimer and empty corpus; Ask disabled with “LLM not configured”.

### UI in this phase

Header + empty states (“No documents indexed”). No fake percentages.

### Exit criteria

- App runs locally
- Disclaimer visible
- No model string literals in code
- Groq adapter is the only LLM implementation, behind an interface

### Out of scope

Collectors, fake reviews, decorative charts, personas.

---

# Phase 1 — Ingestion

### Objective

Bring **publicly and legally accessible** documents into a corpus store with hashes and provenance.

### Depends on

Phase 0 (source register).

### Problem-statement mapping

Corpus definition; Nykaa vs broader; legal collection; weekly incremental hashes (foundation for Phase 10).

### Inputs

- Source register
- Public endpoints/APIs/exports allowed by ToS and robots

### Outputs

- `Document` rows with raw text, URL, hash, scope
- Per-source last_success / last_error

### Components

| Component | Role |
| --- | --- |
| `Collector` interface | `fetch_new(since, seen_hashes) -> DocumentDraft[]` |
| Per-source adapters | Play, App, Reddit, etc. |
| Ingest job | Persist, skip known hashes |
| Collection policy | Abort if login, paywall, CAPTCHA, or robots disallow |

### Step-by-step

1. For each source with `collection_mode = automated`:
   - Fetch only public content via the approved method.
   - Compute `content_hash` (and optionally URL-normalised id).
   - Drop hashes already in the store.
   - Stamp `source_scope`.
2. If a source cannot be automated reliably: set `manual_unavailable`. **Do not invent documents. Do not hide the source.**
3. Write ingest log: attempted, inserted, skipped_duplicate, failed.

### Data contract

**Document**

- `document_id`, `source_id`, `url`
- `published_at` (nullable)
- `raw_text`, `content_hash`
- `source_scope`
- `ingested_at`, `run_id` (nullable until Phase 10)

### Failure behaviour

Network/API error: source `last_error` set; other sources continue; overall ingest `partial`.

### UI in this phase

Optional: raw document count and source status (X automated, Y manual). No insights.

### Exit criteria

- At least one automated source has real documents **or** all sources are honestly `manual_unavailable` with zero fake rows
- Duplicate hash is not inserted twice
- Every document has URL or explicit “no URL” + platform id

### Out of scope

Scraping behind login; calling the result “Nykaa internal data”.

---

# Phase 2 — Cleaning, deduplication, relevance, chunking

### Objective

Produce unique, relevant, chunked text suitable for embeddings and retrieval.

### Depends on

Phase 1.

### Problem-statement mapping

Clean/normalise; dedupe; relevance to wishlist-to-purchase discovery; chunking strategy (config).

### Inputs

- Raw documents

### Outputs

- `cleaned_text`
- `relevance`: `relevant` | `not_relevant` | `unknown`
- `Chunk` rows

### Components

| Component | Role |
| --- | --- |
| Normaliser | Encoding, whitespace, boilerplate strip (careful: do not strip user meaning) |
| Deduper | Exact hash + optional near-duplicate |
| Relevance classifier | Rules and/or Groq **with this document’s text as the only content** |
| Chunker | `CHUNK_SIZE`, `CHUNK_OVERLAP`, stable `chunk_id` |

### Step-by-step

1. Clean `raw_text` → `cleaned_text`.
2. Near-duplicate: mark `duplicate_of` rather than delete (audit trail).
3. Classify relevance to: wishlist behaviour, purchase hesitation, fit/styling/price/reviews/occasion/confidence — not generic app crashes unless tied to shopping hesitation.
4. Split relevant (and optionally unknown) docs into chunks; store ordinal.
5. Default retrieval corpus = chunks from `relevance = relevant`.

### Data contract

**Chunk**

- `chunk_id`, `document_id`, `ordinal`, `text`, `token_count`
- `embedding_version` (null until Phase 3)

### Failure behaviour

Classifier/Groq fail: mark `relevance = unknown`, exclude from default Ask retrieval, include in Coverage & Gaps later (“unclassified count”).

### UI in this phase

Counts: ingested vs relevant vs duplicate. No themes yet.

### Exit criteria

- Chunks exist for relevant docs
- Irrelevant docs excluded from default retrieval
- Duplicates do not double-count in later N

### Out of scope

Opportunity board; answering user questions.

---

# Phase 3 — Embeddings and vector index

### Objective

Make chunks searchable with semantic similarity, lexical keyword matching, and multi-attribute metadata filters.

### Depends on

Phase 2 (Cleaned, relevant chunks).

### Problem-statement mapping

Embeddings → vector DB; hybrid retrieval strategy; top-K selection; incremental index; grounding provenance.

### Best Retrieval Strategy: Hybrid Search (Vector + BM25) + Hard Metadata Scoping

The engine employs a **4-Stage Hybrid Retrieval Strategy** tailored to mixed short app reviews and long conversational Reddit discussions:

1. **Stage 1: Pre-Retrieval Metadata Scoping**:
   - Filter candidate chunks prior to similarity scoring based on query filters: `source_scope` (`nykaa` vs `broader_fashion`), `source_id`, `source_type` (`app_reviews` vs `community_discussion`), and publication date ranges (`published_after`, `published_before`).

2. **Stage 2: Dual-Branch Candidate Retrieval**:
   - **Dense Semantic Vector Search**: 384-dimensional cosine similarity across L2-normalized vectors to capture conceptual intent, emotional hesitation, and paraphrased shopping psychology.
   - **Sparse BM25 / Lexical Keyword Search**: Term-frequency overlap to anchor exact brand names (*"Likha"*, *"Gajra Gang"*, *"Nykd"*), specific garment types (*"anarkali"*, *"kurta"*, *"saree"*), and exact sizing strings (*"32B"*, *"UK 6"*, *"XS vs S"*).

3. **Stage 3: Hybrid Score Blending & Deduplication Gating**:
   - Scores are combined via weighted reciprocal fusion:
     $$\text{FinalScore} = (0.65 \times \text{VectorCosineSimilarity}) + (0.35 \times \text{LexicalMatchScore})$$
   - **Deduplication Gating**: Chunks flagged with `duplicate_of` are suppressed to prevent over-representing near-duplicate reviews.

4. **Stage 4: Top-K Context Window Selection**:
   - Selects top $K=5$ (configurable via `RETRIEVAL_TOP_K`) highest-scoring, cited chunks to supply Phase 4 Grounded RAG with high-density, unpolluted evidence.

### Inputs

- Chunks without embeddings (or stale `embedding_version`)

### Outputs

- Vectors in vector DB (`chunk_vectors` table)
- Metadata: `chunk_id`, `document_id`, `source_id`, `source_type`, `source_scope`, `published_at`, `token_count`

### Components

| Component | Role |
| --- | --- |
| `Embedder` (`TextEmbedder`) | Dense 384-dim semantic embedding with deterministic LSA/SVD projection and L2 normalization |
| `VectorStore` | SQLite vector table (`chunk_vectors`) with BLOB storage, metadata indexing, and in-memory matrix cache |
| `Indexer` (`VectorIndexer`) | Incremental batch indexing checking `embedding_version` |
| `Retriever` (`VectorRetriever`) | Hybrid search engine (0.65 Vector + 0.35 Lexical) with metadata filter enforcement |

### Step-by-step

1. Select chunks where embedding missing or version ≠ current `EMBEDDING_MODEL`.
2. Embed in batches (batch size 128); store version string on chunk.
3. Upsert to vector DB (`chunk_vectors`) with full filter metadata.
4. Do **not** re-embed entire corpus unless model version changed.
5. In-memory matrix cache loaded on startup for sub-millisecond similarity scans.

### Data contract

**Chunk Vector (`chunk_vectors`)**

- `chunk_id` (PRIMARY KEY), `document_id`, `vector` (BLOB float32), `dim` (384)
- `embedding_model`, `source_scope`, `source_id`, `source_type`, `published_at`, `token_count`, `indexed_at`

### Failure behaviour

- Embed API / process fail: retry batch; do not delete old vectors; log failed `chunk_id`s in `indexing_logs`.
- Empty query: return empty list without raising exceptions.

### UI in this phase

- Stack panel shows: Index size (vector count), active embedding model name, retrieval strategy (`hybrid`), and last index update timestamp.

### Exit criteria

- Semantic search returns real `chunk_id`s with verified similarity scores.
- Filter by `source_scope` and `source_type` strictly isolates candidate sets.
- Incremental indexing is idempotent (0 new vectors on re-run).
- Changing `EMBEDDING_MODEL` triggers a new version without silent mixing.

### Out of scope

- Natural-language answer generation, LLM synthesis, or automated business insights.

---

# Phase 4 — Grounded RAG (core)

### Objective

A working Ask API that returns **structured, cited** discovery JSON from retrieved chunks only. This is the architectural heart. Later UI (Phase 9) is a skin on this API.

### Depends on

Phases 0 and 3. Groq adapter from Phase 0.

### Problem-statement mapping

RAG requirements; evidence discipline; metric limitations; Groq grounding flow; Groq fallback; citation inspector data; discount refusal; insufficient evidence.

### Inputs

- User question (or internal job question)
- Optional filters
- Vector index

### Outputs

- Structured discovery response
- `QueryTrace`
- Error or insufficient-evidence objects

### Components

| Component | Role |
| --- | --- |
| Monetary detector | Regex/classifier before retrieve |
| Query processor | Optional retrieval rewrite; must not add facts |
| Retriever | Vector / hybrid, top-K, filters |
| Prompt builder | System rules + numbered chunks only |
| Groq generate | Structured output |
| Grounding validator | Every quote ⊆ some retrieved chunk |
| Confidence scorer | Coverage, source diversity, retrieval scores, consistency → High/Medium/Low |

### Step-by-step

```text
Question + filters
    → if monetary intent: return refusal string (no Groq)
    → process query
    → retrieve top-K chunks
    → if none / very low scores:
         return Insufficient evidence
         (corpus contains X; missing Y; research/data needed Z)
    → if majority broader_fashion:
         flag must_disclose_nykaa_limit
    → prompt = rules + chunks
    → Groq
    → if Groq error: error payload; do not answer
    → validate quotes
    → attach evidence objects (snippet, platform, type, date, URL, relevance)
    → persist QueryTrace
```

**System rules to include in the prompt (not optional):**

- Separate evidence / pattern / inference / hypothesis
- Do not claim 30-day conversion rates
- Do not claim users abandoned wishlists unless the chunk says so
- Label metric hops Observed / Inferred / Unknown
- If conflict, say so rather than averaging opinions

**Required JSON shape**

- `grounded_answer`
- `evidence[]` (3–5): snippet, source, platform, source_type, date, url, retrieval_relevance, chunk_id
- `pattern`
- `inference` (explicitly inference)
- `confidence`
- `evidence_gap`
- `metric_connection`: hops on Wishlist → Reconsideration → Confidence → Cart → Purchase → 30-day conversion, each `observed` | `inferred` | `unknown`
- `related_opportunity_ids` (empty until Phase 7)
- `nykaa_evidence_limited`: boolean + disclaimer text when true
- `conflict`: optional both-sides evidence

**Refusal copy (monetary):**

> Monetary incentives are outside the project scope. I can instead identify evidence-backed non-monetary barriers and opportunities that may influence wishlist-to-purchase conversion.

**Insufficient corpus copy:**

> The indexed corpus does not provide sufficient evidence to answer this directly.

Plus what primary research or product data would be required.

### Failure behaviour

| Case | Behaviour |
| --- | --- |
| Groq 429/5xx | Clear error; index UI still works; log trace |
| Validator fail | Strip bad claims or fail the answer; never keep ungrounded quote |
| Empty retrieve | Insufficient evidence, not Groq essay |

### UI in this phase

Minimal Ask box acceptable (debug). Full page is Phase 9.

### Exit criteria

- Held-out test: model cannot output a sentence in quotes that is not in retrieved text
- Groq disabled: Ask shows error, Overview still lists documents
- Monetary question never hits Groq

### Out of scope

Word clouds; opportunity ranking; weekly scheduler.

---

# Phase 5 — Structured extraction

### Objective

Attach structured attributes to each **relevant** document for taxonomies and later counts.

### Depends on

Phases 2 and 4 (reuse Groq + “context = this document only”).

### Problem-statement mapping

Structured extraction; wishlist behaviour taxonomy; purchase barriers; Other/emerging theme.

### Inputs

- Relevant documents (cleaned text)

### Outputs

- `Extraction` per document (sparse)

### Components

- Extraction prompt + JSON schema
- Enum allow-lists + `other_emerging` string
- Null-if-unsupported policy

### Step-by-step

1. For each relevant document without extraction (incremental):
   - Send **only that document’s text** to Groq.
   - Fill fields only when explicit.
2. Wishlist behaviour: genuine purchase intent | bookmark/save-for-later | compare alternatives | future occasion | waiting/timing | need more information | inspiration | price monitoring | other.
3. Barriers: fit/size | quality | product-vs-image | styling | decision paralysis | price/timing | availability | social validation | reviews/information | occasion/timing | trust | other emerging.
4. Never set “genuine purchase intent” only because the word wishlist appears.
5. Persist `evidence_strength` for the extraction itself.

### Data contract

Nullable: product/category, user_behaviour, wishlist_behaviour, purchase_intent, purchase_stage, barrier, uncertainty, user_job, workaround, external_information_source, alternative_considered, occasion, fit_size, styling, price, reviews_social_validation, availability, quality_expectation, other_new_theme, evidence_strength.

### Failure behaviour

Groq fail: skip document, retry next run; do not backfill with guesses.

### UI in this phase

Optional debug table. Production UI in Phase 8 executive summary.

### Exit criteria

- Manual audit of 20 docs: no forced categories
- New themes appear under other/emerging, not dropped

### Out of scope

Population statistics; scoring opportunities.

---

# Phase 6 — Quantification

### Objective

Compute honest, denominator-bearing corpus statistics.

### Depends on

Phase 5 (and relevant document set from Phase 2).

### Problem-statement mapping

Quantification; Coverage & Gaps; Ask “Quantify this”; no population claims.

### Inputs

- Documents + extractions
- Relevant analysed set definition (document explicitly)

### Outputs

- Theme mention counts
- Share of relevant analysed documents (with N)
- Source distribution, theme distribution, segment distribution, cross-source consistency
- Coverage & Gaps records

### Components

- Aggregation jobs
- Copy templates that inject N
- Gap catalogue (static + computed): e.g. no user-level 30-day conversion in UGC

### Step-by-step

1. Define `N` = count of relevant analysed documents in the current snapshot.
2. For each theme/barrier/behaviour: count documents with that extraction (not chunks, unless documented).
3. Share = count / N, store both.
4. Cross-source: number of `source_type`s in which the theme appears.
5. Segment splits only if extraction support exists; else flag insufficient segmentation.

**Allowed:** Fit uncertainty appears in 27% of relevant analysed documents (N=1,842).  
**Forbidden:** 27% of Nykaa users have fit problems.

### Failure behaviour

N = 0: show empty state, no 0% fake precision.

### UI in this phase

Can power Overview counts; polish in Phase 8.

### Exit criteria

- API refuses to return a percentage without `n`
- 30-day conversion rate is **not** a computed metric; it is a documented gap

### Out of scope

Calling stats “Nykaa analytics”.

---

# Phase 7 — Opportunities, scoring, metric journey

### Objective

Turn patterns into a ranked **research shortlist** with citations and a transparent score.

### Depends on

Phases 4–6.

### Problem-statement mapping

Opportunity identification, scoring, board fields, journey visualisation, Explore Evidence, non-monetary intervention type only.

### Inputs

- Extractions, stats, ability to retrieve example chunks per theme

### Outputs

- `Opportunity` records + ranks + snapshot for evolution

### Components

| Component | Role |
| --- | --- |
| Clusterer | Themes → opportunity candidates |
| Evidence picker | 3–5 strongest chunks per opportunity |
| Scorer | Six 1–5 scores + weighted total |
| Journey builder | Hops with observed/inferred/unknown |
| Explore Evidence query | Related chunks, distributions, conflicts, related questions |

### Step-by-step

1. Group recurring barriers/behaviours into opportunity candidates.
2. For each, fill:
   - Problem name (one line)
   - User job
   - Blocker
   - Evidence (3–5 chunk refs)
   - Scale (count and/or share of relevant corpus + N)
   - Metric connection on Wishlist → Reconsideration → Confidence → Cart → Purchase; each hop labelled
   - Current workaround
   - Confidence High/Medium/Low
   - Evidence gap
   - Research hypothesis for interviews
   - Non-monetary intervention **type** (not a spec’d feature, not a discount)
3. Score 1–5: frequency, metric relevance, user pain/behavioural impact, evidence strength, cross-source consistency, AI/product solvability (non-monetary).
4. `research_prioritisation_score = weighted sum`. Store weights in config. Show components in UI.
5. Rank descending. Rank 1 label: **Recommended opportunity to validate**. Status field `validate_next`.
6. Journey graphic: Wishlist added → Reconsideration → [Barrier] → postponed/alternative → no purchase within 30 days.

### Data contract

All board card fields plus `score_frequency`, `score_metric_relevance`, `score_pain`, `score_evidence`, `score_cross_source`, `score_solvability`, `research_prioritisation_score`, `rank`, `snapshot_id`.

### Failure behaviour

Groq clustering fail: keep previous snapshot; WeeklyRun `partial`; do not invent opportunities.

### UI in this phase

Opportunity Board can go live (Phase 8 polish). Explore Evidence drawer/page.

### Exit criteria

- No card titled Final problem
- 30-day hop is `unknown` unless a cited chunk explicitly supports it
- Explore Evidence resolves Opportunity → Claim → Evidence → Source

### Out of scope

Shipping a product solution; discount strategy.

---

# Phase 8 — Dashboard (Overview, Board, Explorer)

### Objective

PM-style research intelligence UI for corpus, summary, board, comparison, segments, evidence, citations.

### Depends on

Phases 6–7 for real data; Phase 0 shell.

### Problem-statement mapping

Dashboard layout A–G; UX principles; citation inspector; weak evidence display on overview gaps.

### Inputs

- APIs from Phases 1–7, 10 (weekly fields stubbed until Phase 10)

### Outputs

- Overview page
- Opportunity Board page/section
- Evidence explorer
- Citation inspector
- Source comparison filters
- Segment panel

### Step-by-step (page composition)

**A. Header** — as Phase 0, plus live stack from env.

**B. Corpus overview**

- Total documents indexed, relevant documents, source types, date coverage, theme count, segment count
- Coverage & Gaps
- Weekly run placeholders until Phase 10
- Evolution strip: Previous corpus → New evidence → Updated themes → Updated opportunities (populated Phase 10)

**C. Executive discovery summary**

- Top wishlist behaviours
- Top purchase barriers
- Top uncertainties
- Top workarounds
- Important evidence gaps

**D. Opportunity Board** — most prominent; cards from Phase 7.

**E. Platform/source comparison** — filters: source, source type, time, theme, segment, intent. Third-party ≠ Nykaa internal.

**F. Segments** — intent, shopper type, occasion, category, or other evidence-backed only. Else: **Insufficient evidence for reliable segmentation.**

**G. Evidence explorer** — snippet, source, source type, date, URL, relevance score.

**Citation inspector** — click claim → passages → source → date → URL. No evidence → claim is not shown.

### UX rules

Prioritise hierarchy, evidence visibility, explainability, comparability, short answers, drill-down, fact vs inference.  
Avoid word clouds, generic sentiment charts, decorative AI, long essays, unsupported %, fake precision, unsupported personas.

### Failure behaviour

API down: empty/error banners; do not show cached invented insights.

### Exit criteria

Evaluator can walk: conversations → behaviours → barriers → patterns → quantified themes → opportunity comparison → highest-priority opportunity → evidence → metric connection → research hypothesis.

### Out of scope

Chat-style infinite thread (that is Phase 9).

---

# Phase 9 — Ask the Discovery Engine (dedicated page)

### Objective

Primary conversational research interface on top of the Phase 4 API.

### Depends on

Phases 4 and 7 (related opportunities); Phase 8 navigation.

### Problem-statement mapping

Dedicated Ask page; 10 questions; filters; follow-ups; answer sections; evidence strength on presets; follow-up actions; visible reasoning chain.

### Inputs

- Phase 4 API
- Preset question catalogue
- Filters
- Opportunity ids for “related”

### Outputs

- Ask page UX
- Session follow-ups (same grounding rules)
- Evidence-strength badges on presets

### Components

- Question input + follow-up thread
- Ten one-click prompts:
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
- Badge job: for each preset, estimate evidence strength (strong / moderate / weak) from retrieval hit quality and extraction coverage — **not** by asking Groq to invent coverage
- Example: **30-day wishlist behaviour: Weak evidence** — public conversations do not contain user-level data that a wishlisted item was purchased within 30 days
- Follow-up chips (each is a new grounded RAG call):
  - Show more evidence
  - Quantify this
  - Compare sources
  - Compare segments
  - Find contradictory evidence
  - Explain the pattern
  - What don’t we know?
  - What should I validate in interviews?

### Step-by-step (one question)

1. User asks or clicks preset (filters applied).
2. Phase 4 pipeline.
3. Render **separate sections**: Grounded Answer, Evidence, Pattern, Inference, Confidence, Evidence Gap, Metric Connection, Related Opportunities.
4. Do not collapse into one generated essay.
5. Click evidence → citation inspector.
6. Click related opportunity → board / Explore Evidence.

**Visible journey:** Question → Grounded Answer → Evidence → Pattern → Inference → Metric Connection → Potential Opportunity → Research Hypothesis → Interview Validation.

### Failure behaviour

Same as Phase 4. Weak preset: show badge + gap; **do not fabricate** a strong answer.

### Exit criteria

- Dedicated route, not a sidebar widget only
- All 10 presets present with strength indicators
- Follow-ups do not skip retrieval

### Out of scope

Auto-declaring the interview script as the final problem.

---

# Phase 10 — Conflicts, Coverage Ops & Weekly Incremental Pipeline

### Objective

Establishes the Nykaa Fashion Discovery Engine as an ongoing, automated research intelligence system with weekly Monday incremental pipelines, honest source status registers, and conflict presentation.

### Depends on

Phases 1–7, 8 (overview fields).

### Problem-statement mapping

Weekly Monday pipeline; Weekly Research Run UI; GitHub Actions flow; incremental processing; conflict handling; corpus evolution.

### Inputs

- Existing hashes/ids
- Collectors from Phase 1
- Downstream jobs from Phases 2–7

### Outputs

- `WeeklyRun` records
- Updated index and opportunity snapshot
- Overview run panel
- Conflict presentation on Ask and Explore Evidence

### Weekly step-by-step (Monday morning)

```text
GitHub Actions (or equivalent) scheduled workflow
      ↓
Source collectors (new public items only)
      ↓
Hash/ID gate — skip processed
      ↓
Data cleaning + deduplication
      ↓
Relevance classification
      ↓
Structured evidence extraction
      ↓
Embeddings / vector index upsert (new chunks only)
      ↓
Recount themes / opportunities
      ↓
Re-run opportunity analysis and prioritisation
      ↓
Dashboard snapshot + evolution diff
      ↓
Research corpus updated + WeeklyRun log
```

**WeeklyRun fields**

- Last updated (datetime)
- Next scheduled run (datetime)
- New documents this week (count)
- New relevant documents (count)
- Sources successfully updated X / Y
- Sources with errors X
- Analysis status: Success / Partial / Failed
- Per-source results, processing errors, analysis timestamp
- Last successful run pointer

**Persist always:** processed document IDs/hashes, failed sources, Groq failure on analysis (do not delete index).

**Conflicts:** if retrieved/extracted viewpoints disagree, UI: **Conflicting evidence detected**, show both sides, do not synthesise a false consensus. If unresolvable: **Additional primary research is required.**

**Overview evolution:** Previous corpus → New evidence → Updated themes → Updated opportunities.

### Failure behaviour

| Case | Status |
| --- | --- |
| One source fails, rest OK | Partial; failed source listed |
| Groq down during analysis | Failed or Partial; previous board retained; evidence still browsable |
| Source not automatable | `manual_unavailable`; counted in Y, not silently omitted |

### UI in this phase

Overview must show whether the **latest weekly research run succeeded**.

### Exit criteria

- Simulated second week only processes new hashes
- Manual sources visible
- No full-corpus re-embed unless embedding model changed

### Out of scope

Bypassing robots to “complete” X/Y.

---

# Phase 11 — Hardening, documentation, polish

### Objective

Ship a functional, explainable, deployable system with a complete README.

### Depends on

Phases 0–10 working on a real (even small) corpus.

### Problem-statement mapping

Expected deliverables; success criteria; UX polish last; known limitations.

### Inputs

- Working pipeline and dashboard

### Outputs

- README: setup, corpus notes, architecture pointer, scoring formula and weights, limitations, weekly scheduler, incremental index, source status, Groq/model/embeddings/vector DB/retrieval/chunking/top-K, env config
- Production error states
- Visual polish without violating UX bans

### Step-by-step

1. Write README from live config, not from memory.
2. Rate-limit handling: backoff on Groq; still no ungrounded fallback.
3. Review UI against banned patterns (sentiment-only charts, word clouds, fake personas).
4. Confirm Groq outage path with a chaos test (invalid key).
5. Confirm discount query path.
6. Confirm 10th preset / 30-day question shows **weak evidence** honestly.

### Exit criteria (product success)

A Growth PM can see **which user problems are most worth investigating** for 30-day wishlist-to-purchase conversion, with every important conclusion traceable to real evidence.

Ask path works: Question → Grounded Answer → Evidence → Pattern → Inference → Metric Connection → Opportunity → Research Hypothesis → Interview Validation.

### Out of scope

Primary interviews themselves; locking a product solution.

---

# Phase 12 — Streamlit Deployment

### Objective

Deploy the completed Nykaa Fashion AI Discovery Engine as a user-facing Streamlit application.

### Purpose

Deploy the completed Nykaa Fashion AI Discovery Engine as a user-facing Streamlit application for public portfolio demonstration and interactive PM research intelligence exploration.

### Depends on

Phases 0–11 completed and hardened.

### Scope

- **Streamlit Presentation Layer**: Streamlit acts as the final presentation/deployment layer.
- **Application Entry Point**: Deployment of `phase11/app.py`.
- **Full Discovery Features**: PM Dashboard and Ask Engine accessible through the deployed Streamlit application.
- **Service Integration**: Existing Phase 8/9 services (`DashboardService`, `AskSessionService`) remain the core application/service layer.
- **Data Persistence**: SQLite database (`data/discovery_engine.db`) and vector-store artifacts (`data/vector_store/`) must be available to the deployed application.
- **Secure Environment Variables**: Required environment variables/secrets configured securely via deployment secrets.
- **Optional LLM API Key**: Groq API key remains optional because deterministic vector fallback exists.
- **No FastAPI Deployment Needed**: No FastAPI server deployment is required for the Streamlit application.
- **Guardrails Preserved**: Deployment preserves all existing evidence-grounding, non-monetary policy, and product guardrails.
- **Independent Automated Pipeline**: GitHub Actions weekly Monday pipeline remains independent of the Streamlit UI.

### Architecture

```text
Streamlit Cloud / Streamlit Deployment
                  ↓
          `phase11/app.py`
                  ↓
DashboardService + AskSessionService
                  ↓
         Phases 1–10 services
                  ↓
        SQLite + Vector Store
```

### Deployment Goal

- Make the completed Part 1 Discovery Engine publicly accessible for portfolio demonstration.
- Verify the deployed application loads successfully and can execute the major dashboard/Ask flows.

---

# Phase dependency graph

```text
Phase 0 Foundation
    │
    ▼
Phase 1 Ingestion
    │
    ▼
Phase 2 Clean / relevance / chunk
    │
    ▼
Phase 3 Embed / vector index
    │
    ▼
Phase 4 Grounded RAG API ◄── Groq adapter (from 0)
    │
    ├──────────────► Phase 5 Extraction
    │                     │
    │                     ▼
    │               Phase 6 Quantification
    │                     │
    └────────► Phase 7 Opportunities ◄──┘
                    │
                    ▼
              Phase 8 Dashboard
                    │
                    ▼
              Phase 9 Ask page
                    │
                    ▼
              Phase 10 Weekly + conflicts
                    │
                    ▼
              Phase 11 README + polish
                    │
                    ▼
              Phase 12 Streamlit Deployment
```

---

# Groq usage by phase (quick reference)

| Phase | Allowed Groq use | Context window content |
| --- | --- | --- |
| 0 | Connectivity check optional | None / ping |
| 2 | Relevance classification | One document |
| 4, 9 | Answer, pattern, inference, follow-ups, synthesis | Retrieved chunks only |
| 5 | Attribute extraction | One document |
| 7, 10 | Opportunity analysis | Retrieved or extracted slices, cited |
| 1, 3, 6, 8, 11 | Prefer no generation | — |

---

# Implementation order (do not overbuild)

1. Evidence grounding (Phase 4)  
2. Structured extraction (Phase 5)  
3. Opportunity identification (Phase 7 start)  
4. Quantification (Phase 6)  
5. Opportunity scoring (Phase 7)  
6. Metric connection (Phase 7)  
7. Citation inspector (Phases 4, 8)  
8. Coverage/gaps (Phases 6, 8, 10)  
9. Dashboard UX (Phases 8–9)  
10. Visual polish (Phase 11)

---

# What no phase is allowed to ship

- Final problem / confirmed root cause / proven 30-day failure reason  
- Fake 30-day conversion KPIs  
- Discount/coupon/cashback playbooks  
- Ungrounded Groq answers  
- Silent omission of failed or manual sources  
- Third-party UGC labelled as Nykaa internal data  

Interviews (5–6 users) remain **outside** this architecture. This system only produces the evidence-backed shortlist.
