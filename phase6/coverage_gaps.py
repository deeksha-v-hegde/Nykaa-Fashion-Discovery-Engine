import logging
from typing import Any, Dict, List

from phase6.models import CoverageGapItem
from phase6.store import Phase6Store, get_db_connection, init_phase6_schema

logger = logging.getLogger("phase6.coverage_gaps")


class CoverageGapsEngine:
    """
    Phase 6 Coverage & Gaps Engine.
    Catalogs structural data gaps (30-day conversion tracking gap, non-monetary exclusion)
    and computes corpus coverage metrics.
    """

    @staticmethod
    def get_gap_catalogue() -> List[CoverageGapItem]:
        init_phase6_schema()

        # Structural Gaps (Static & Enforced)
        gaps = [
            CoverageGapItem(
                gap_id="gap_30day_conversion",
                category="Structural Gap",
                title="Missing Longitudinal Tracking for 30-Day Wishlist Conversion",
                description="Public reviews and Reddit discussions do not contain user-level tracking to confirm whether a saved wishlist item was purchased within 30 days.",
                impact="30-day wishlist-to-purchase conversion rate cannot be computed from public UGC; metric hop strictly labeled 'unknown'.",
                recommended_action="Conduct 5–6 qualitative user interviews or instrument internal product analytics cohort tracking.",
                status="Active"
            ),
            CoverageGapItem(
                gap_id="gap_monetary_exclusion",
                category="Structural Gap",
                title="Monetary Interventions Excluded by System Policy",
                description="Discounts, coupons, promo codes, price drops, and cashbacks are excluded from discovery analysis by project constraint.",
                impact="Forces product discovery to focus on non-monetary root causes (sizing, fabric clarity, styling context, delivery friction).",
                recommended_action="Explore non-monetary product features (standardized size charts, user review photos, delivery SLAs).",
                status="Active"
            ),
            CoverageGapItem(
                gap_id="gap_manual_sources_unavailable",
                category="Corpus Gap",
                title="Manual / Unavailable Source Registers (YouTube, X, Forums)",
                description="Automated weekly scrapers for YouTube, X (Twitter), and Fashion Forums are set to manual/unavailable to respect robots.txt and API access limits.",
                impact="Corpus evidence is drawn primarily from Google Play Store, Apple App Store, and Reddit (r/IndianFashionAddicts, r/TwoXIndia).",
                recommended_action="Incorporate periodic manual data drops or official API connectors for social video hauls.",
                status="Active"
            ),
            CoverageGapItem(
                gap_id="gap_emerging_custom_themes",
                category="Emerging Theme",
                title="144 Documents with Novel / Emerging Custom Themes",
                description="144 relevant documents describe friction points outside the initial 12 seed barrier taxonomies (e.g. app navigation glitches, post-shipment lockouts).",
                impact="Surfaced under 'other_new_theme' for taxonomy evolution without dropping valid user mentions.",
                recommended_action="Review emerging theme text snippets to expand seed taxonomy in future pipeline runs.",
                status="Active"
            )
        ]

        return gaps

    @staticmethod
    def compute_corpus_coverage() -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents")
        total_ingested = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'relevant' AND duplicate_of IS NULL")
        relevant_canonical_n = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'not_relevant'")
        not_relevant_cnt = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'unknown'")
        unknown_cnt = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE duplicate_of IS NOT NULL")
        near_duplicates_cnt = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunk_vectors")
        total_vectors = cursor.fetchone()[0]

        conn.close()

        return {
            "total_ingested_documents": total_ingested,
            "sample_size_n": relevant_canonical_n,
            "not_relevant_documents": not_relevant_cnt,
            "unknown_documents_retained": unknown_cnt,
            "near_duplicates_flagged": near_duplicates_cnt,
            "total_retrieval_chunks": total_chunks,
            "persisted_vectors": total_vectors,
            "analysed_coverage_pct": round((relevant_canonical_n / total_ingested) * 100, 1) if total_ingested > 0 else 0.0
        }
