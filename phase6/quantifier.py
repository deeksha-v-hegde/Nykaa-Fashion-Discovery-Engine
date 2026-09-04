import logging
from typing import Any, Dict, List

from phase6.models import QuantificationReport, ScopeDistribution, StatItem
from phase6.store import get_db_connection, init_phase6_schema

logger = logging.getLogger("phase6.quantifier")


class CorpusQuantifier:
    """
    Phase 6 Corpus Quantifier.
    Computes honest, denominator-bearing statistics over canonical relevant documents.
    
    Guarantees:
    - Every percentage/share is explicitly tied to sample size N.
    - Zero population claims (e.g. 'X% of Nykaa users' is strictly forbidden).
    - Safe handling of N = 0 (returns clean empty state without ZeroDivisionError).
    - Cross-source consistency calculation.
    """

    def compute_quantification(self) -> QuantificationReport:
        init_phase6_schema()
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Compute Sample Size N (Canonical Relevant Documents)
        cursor.execute("""
            SELECT COUNT(*)
            FROM documents
            WHERE relevance = 'relevant' AND duplicate_of IS NULL
        """)
        sample_size_n = cursor.fetchone()[0]

        if sample_size_n == 0:
            logger.info("Sample size N = 0. Returning clean empty quantification state.")
            conn.close()
            return QuantificationReport(
                snapshot_id="empty",
                sample_size_n=0,
                barriers=[],
                wishlist_behaviours=[],
                categories=[],
                scope_distribution=ScopeDistribution(
                    nykaa_count=0,
                    nykaa_share_pct=0.0,
                    broader_count=0,
                    broader_share_pct=0.0,
                    total_n=0,
                    formatted_text="No relevant documents analyzed (N=0)."
                ),
                evidence_strengths={"high": 0, "medium": 0, "low": 0},
                emerging_themes_count=0
            )

        # 2. Barrier Distribution & Cross-Source Consistency
        cursor.execute("""
            SELECT 
                e.barrier, 
                COUNT(DISTINCT e.document_id) as cnt,
                COUNT(DISTINCT s.source_type) as cross_sources,
                GROUP_CONCAT(DISTINCT s.source_type) as source_type_list
            FROM document_extractions e
            JOIN documents d ON e.document_id = d.document_id
            JOIN sources s ON d.source_id = s.source_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL AND e.barrier IS NOT NULL
            GROUP BY e.barrier
            ORDER BY cnt DESC
        """)
        barrier_rows = cursor.fetchall()
        barriers: List[StatItem] = []

        for r in barrier_rows:
            key = r["barrier"]
            count = r["cnt"]
            share_pct = round((count / sample_size_n) * 100, 1)
            sources = r["source_type_list"].split(",") if r["source_type_list"] else []

            low_sample_note = " [Low sample size, N<20]" if sample_size_n < 20 else ""
            formatted = f"{key.replace('_', ' ').title()} appears in {share_pct}% of relevant analysed documents (N={sample_size_n:,}){low_sample_note}."

            barriers.append(StatItem(
                key=key,
                count=count,
                sample_size_n=sample_size_n,
                share_pct=share_pct,
                formatted_text=formatted,
                cross_source_consistency=r["cross_sources"],
                source_types=sources
            ))

        # 3. Wishlist Behaviour Distribution
        cursor.execute("""
            SELECT 
                e.wishlist_behaviour, 
                COUNT(DISTINCT e.document_id) as cnt,
                COUNT(DISTINCT s.source_type) as cross_sources,
                GROUP_CONCAT(DISTINCT s.source_type) as source_type_list
            FROM document_extractions e
            JOIN documents d ON e.document_id = d.document_id
            JOIN sources s ON d.source_id = s.source_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL AND e.wishlist_behaviour IS NOT NULL
            GROUP BY e.wishlist_behaviour
            ORDER BY cnt DESC
        """)
        wishlist_rows = cursor.fetchall()
        wishlist_behaviours: List[StatItem] = []

        for r in wishlist_rows:
            key = r["wishlist_behaviour"]
            count = r["cnt"]
            share_pct = round((count / sample_size_n) * 100, 1)
            sources = r["source_type_list"].split(",") if r["source_type_list"] else []
            formatted = f"{key.replace('_', ' ').title()} appears in {share_pct}% of relevant analysed documents (N={sample_size_n:,})."

            wishlist_behaviours.append(StatItem(
                key=key,
                count=count,
                sample_size_n=sample_size_n,
                share_pct=share_pct,
                formatted_text=formatted,
                cross_source_consistency=r["cross_sources"],
                source_types=sources
            ))

        # 4. Product Category Distribution
        cursor.execute("""
            SELECT 
                e.product_category, 
                COUNT(DISTINCT e.document_id) as cnt
            FROM document_extractions e
            JOIN documents d ON e.document_id = d.document_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL AND e.product_category IS NOT NULL
            GROUP BY e.product_category
            ORDER BY cnt DESC
        """)
        cat_rows = cursor.fetchall()
        categories: List[StatItem] = []

        for r in cat_rows:
            key = r["product_category"]
            count = r["cnt"]
            share_pct = round((count / sample_size_n) * 100, 1)
            formatted = f"{key} appears in {share_pct}% of relevant analysed documents (N={sample_size_n:,})."

            categories.append(StatItem(
                key=key,
                count=count,
                sample_size_n=sample_size_n,
                share_pct=share_pct,
                formatted_text=formatted
            ))

        # 5. Scope Distribution (Nykaa vs Broader Fashion)
        cursor.execute("""
            SELECT s.source_scope, COUNT(DISTINCT d.document_id) as cnt
            FROM documents d
            JOIN sources s ON d.source_id = s.source_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL
            GROUP BY s.source_scope
        """)
        scope_rows = {r["source_scope"]: r["cnt"] for r in cursor.fetchall()}
        nykaa_cnt = scope_rows.get("nykaa", 0)
        broader_cnt = scope_rows.get("broader_fashion", 0)
        nykaa_pct = round((nykaa_cnt / sample_size_n) * 100, 1)
        broader_pct = round((broader_cnt / sample_size_n) * 100, 1)

        scope_dist = ScopeDistribution(
            nykaa_count=nykaa_cnt,
            nykaa_share_pct=nykaa_pct,
            broader_count=broader_cnt,
            broader_share_pct=broader_pct,
            total_n=sample_size_n,
            formatted_text=f"Nykaa scope: {nykaa_pct}% ({nykaa_cnt:,} docs), Broader fashion: {broader_pct}% ({broader_cnt:,} docs) out of N={sample_size_n:,} relevant analysed documents."
        )

        # 6. Evidence Strengths
        cursor.execute("""
            SELECT e.evidence_strength, COUNT(DISTINCT e.document_id) as cnt
            FROM document_extractions e
            JOIN documents d ON e.document_id = d.document_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL
            GROUP BY e.evidence_strength
        """)
        strengths = {r["evidence_strength"]: r["cnt"] for r in cursor.fetchall()}

        # 7. Emerging Custom Themes Count
        cursor.execute("""
            SELECT COUNT(DISTINCT e.document_id)
            FROM document_extractions e
            JOIN documents d ON e.document_id = d.document_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL AND e.other_new_theme IS NOT NULL
        """)
        emerging_cnt = cursor.fetchone()[0]

        conn.close()

        return QuantificationReport(
            snapshot_id="draft",
            sample_size_n=sample_size_n,
            barriers=barriers,
            wishlist_behaviours=wishlist_behaviours,
            categories=categories,
            scope_distribution=scope_dist,
            evidence_strengths=strengths,
            emerging_themes_count=emerging_cnt
        )
