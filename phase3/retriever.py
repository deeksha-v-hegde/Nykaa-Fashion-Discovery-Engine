import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import numpy as np

from config.settings import Settings
from phase3.embedder import TextEmbedder
from phase3.vector_store import VectorStore


@dataclass
class SearchResult:
    chunk_id: str
    document_id: str
    score: float
    vector_score: float
    lexical_score: float
    text: str
    source_id: str
    source_name: str
    platform: str
    source_scope: str
    source_type: str
    published_at: Optional[str]
    url: str
    token_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VectorRetriever:
    """
    Phase 3 Vector & Hybrid Retriever with Strict Quality & Friction Alignment.
    """

    def __init__(self, embedding_model: Optional[str] = None):
        settings = Settings()
        self.embedding_model = embedding_model or settings.embedding_model or "text-embedding-3-small"
        self.default_strategy = settings.retrieval_strategy  # "vector" or "hybrid"
        self.default_top_k = settings.retrieval_top_k
        self.embedder = TextEmbedder(model_name=self.embedding_model)

    STOP_WORDS = {
        "what", "why", "how", "when", "where", "who", "which", "whose", "whom",
        "the", "a", "an", "and", "or", "but", "if", "because", "as",
        "while", "of", "at", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below", "to",
        "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "all", "any", "both", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
        "will", "just", "don", "should", "now", "are", "is", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "product", "products", "item", "items", "nykaa", "app", "ordered"
    }

    def _compute_lexical_scores(self, query: str, texts: List[str]) -> np.ndarray:
        """
        Computes relevance-weighted lexical matching score across chunk texts
        excluding common stop words and accounting for morphological variants.
        """
        raw_terms = [t.lower() for t in re.findall(r"\b\w+\b", query) if len(t) > 2]
        query_terms = [t for t in raw_terms if t not in self.STOP_WORDS]
        
        # Add base stems for key terms
        stems = set(query_terms)
        for t in query_terms:
            if t.endswith("ed") and len(t) > 4:
                stems.add(t[:-2])
            elif t.endswith("s") and len(t) > 3:
                stems.add(t[:-1])
            elif t.endswith("ing") and len(t) > 5:
                stems.add(t[:-3])
                
        active_terms = list(stems)
        if not active_terms:
            return np.zeros(len(texts), dtype=np.float32)

        scores = np.zeros(len(texts), dtype=np.float32)
        for i, text in enumerate(texts):
            text_lower = text.lower()
            term_hits = sum(1 for term in active_terms if term in text_lower)
            scores[i] = term_hits / len(active_terms)
        return scores

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        strategy: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Performs vector or hybrid search over indexed chunks matching filters.
        """
        if not query or not query.strip():
            return []

        top_k = top_k or self.default_top_k
        strategy = strategy or self.default_strategy
        filters = filters or {}

        # 1. Load vector index from store
        matrix, metadata = VectorStore.load_index_into_memory(self.embedding_model)
        if matrix.shape[0] == 0 or not metadata:
            return []

        # 2. Strict Quality & Relevance Filtering
        candidate_indices: List[int] = []

        # Noise patterns to exclude (OOTD photo checks, thrifted/local market showcases, smartwatch posts)
        ootd_noise_patterns = [
            re.compile(r"\bthrift(ed)?\b", re.IGNORECASE),
            re.compile(r"\blocal\s+(shop|market|store|vendor|tailor)\b", re.IGNORECASE),
            re.compile(r"\bsmartwatch\b", re.IGNORECASE),
            re.compile(r"\brate\s+my\s+fit\b", re.IGNORECASE),
            re.compile(r"\bconfident\s+in\s+this\s+fit\b", re.IGNORECASE),
            re.compile(r"\bbday\s+fit\b", re.IGNORECASE),
        ]

        shopping_intent_keywords = [
            "buy", "buying", "bought", "purchase", "purchasing", "order", "ordering", "ordered",
            "wishlist", "cart", "return", "returns", "refund", "exchange",
            "delivery", "shipping", "brand", "brands", "online", "store",
            "quality", "price", "pricing", "cost", "review", "reviews",
            "size chart", "sizing chart", "true to size", "runs small", "runs large",
            "where to find", "where to buy", "recommend", "recommendation", "recommendations"
        ]

        problem_signal_keywords = [
            "delay", "hesitat", "sizing", "fit", "return", "delivery", "unpredictable",
            "fabric", "see-through", "color", "quality", "support", "c care", "issue",
            "problem", "cancel", "stuck", "doubt", "uncertain", "fear", "wishlist",
            "scam", "worst", "failed", "disappoint", "wrong", "different", "hardest"
        ]

        is_barrier_query = any(k in query.lower() for k in [
            "prevent", "hesitat", "barrier", "friction", "why", "issue",
            "problem", "delay", "doubt", "role", "uncertain", "postpone", "unmet"
        ])

        for idx, m in enumerate(metadata):
            text_words = m["text"].split()
            lower_text = m["text"].lower()

            # Rule 1: Must be at least 15 words long (eliminates short 4-word praise junk)
            if len(text_words) < 15:
                continue

            # Rule 2: Exclude non-shopping OOTD selfie noise and thrifted showcases
            if any(p.search(m["text"]) for p in ootd_noise_patterns):
                continue

            # Rule 3: Broader fashion posts must have explicit e-commerce/shopping intent
            if m["source_scope"] == "broader_fashion":
                if not any(k in lower_text for k in shopping_intent_keywords):
                    continue

            # Rule 4: If query asks about purchase barriers or friction, retrieved chunk must contain a friction signal!
            if is_barrier_query:
                if not any(k in lower_text for k in problem_signal_keywords):
                    continue
                # Exclude purely positive praise reviews from barrier candidate pools
                if any(praise in lower_text for praise in [
                    "amazing shopping experience",
                    "delivery is always on time",
                    "everything i got was perfect",
                    "love shopping on nykaa for last"
                ]):
                    continue

            # Standard Metadata Filters
            if "source_scope" in filters and filters["source_scope"]:
                if m["source_scope"] != filters["source_scope"]:
                    continue
            if "source_id" in filters and filters["source_id"]:
                if m["source_id"] != filters["source_id"]:
                    continue
            if "source_type" in filters and filters["source_type"]:
                if m["source_type"] != filters["source_type"]:
                    continue
            if "published_after" in filters and filters["published_after"]:
                if not m["published_at"] or m["published_at"] < filters["published_after"]:
                    continue
            if "published_before" in filters and filters["published_before"]:
                if not m["published_at"] or m["published_at"] > filters["published_before"]:
                    continue

            candidate_indices.append(idx)

        if not candidate_indices:
            # Fallback candidate indices: strictly enforce minimum 15 words to prevent junk snippets
            candidate_indices = [
                idx for idx, m in enumerate(metadata)
                if len(m["text"].split()) >= 15
            ]

        # Filtered sub-matrix
        sub_matrix = matrix[candidate_indices]
        sub_metadata = [metadata[i] for i in candidate_indices]

        # 3. Vector Cosine Similarity
        query_vec = self.embedder.embed_query(query)
        vector_scores = np.dot(sub_matrix, query_vec)
        vector_scores = np.clip(vector_scores, 0.0, 1.0)

        # 4. Lexical Scoring (if hybrid)
        if strategy == "hybrid":
            candidate_texts = [m["text"] for m in sub_metadata]
            lexical_scores = self._compute_lexical_scores(query, candidate_texts)
            
            # Domain-Specific Wishlist Stage Alignment
            is_wishlist_q = any(k in query.lower() for k in ["wishlist", "wishlisted", "saved item", "saved product"])
            wishlist_boost = np.zeros(len(sub_metadata), dtype=np.float32)
            if is_wishlist_q:
                for i, m in enumerate(sub_metadata):
                    lt = m["text"].lower()
                    if "wishlist" in lt or "wishlisted" in lt or "saved" in lt:
                        wishlist_boost[i] = 0.20
                    elif any(dk in lt for dk in ["fake delivery", "courier partner", "worst customer service", "failed to deliver"]):
                        wishlist_boost[i] = -0.15

            # Weighted hybrid blend (60% semantic vector + 40% exact lexical overlap + domain boost)
            final_scores = 0.60 * vector_scores + 0.40 * lexical_scores + wishlist_boost
        else:
            lexical_scores = np.zeros_like(vector_scores)
            final_scores = vector_scores

        # 5. Top-K Selection
        ranked_indices = np.argsort(final_scores)[::-1][:top_k]

        results: List[SearchResult] = []
        for r_idx in ranked_indices:
            score = float(final_scores[r_idx])
            v_score = float(vector_scores[r_idx])
            l_score = float(lexical_scores[r_idx])
            meta = sub_metadata[r_idx]

            results.append(SearchResult(
                chunk_id=meta["chunk_id"],
                document_id=meta["document_id"],
                score=round(score, 4),
                vector_score=round(v_score, 4),
                lexical_score=round(l_score, 4),
                text=meta["text"],
                source_id=meta["source_id"],
                source_name=meta["source_name"],
                platform=meta["platform"],
                source_scope=meta["source_scope"],
                source_type=meta["source_type"],
                published_at=meta["published_at"],
                url=meta["url"],
                token_count=meta["token_count"]
            ))

        return results
