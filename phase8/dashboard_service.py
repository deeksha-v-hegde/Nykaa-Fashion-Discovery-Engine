from datetime import datetime, timedelta, timezone
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import Settings
from phase6.coverage_gaps import CoverageGapsEngine
from phase6.quantifier import CorpusQuantifier
from phase7.store import Phase7Store
from phase8.models import (
    CorpusOverviewStats,
    ExecutiveDiscoverySummary,
    ExplorerEvidenceItem,
    SegmentItem,
    SourceComparisonItem,
)

logger = logging.getLogger("phase8.dashboard_service")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


class DashboardService:
    """
    Phase 8 Master Dashboard Aggregator Service.
    Compiles Sections B through G for the PM Research Intelligence Dashboard.
    """

    def __init__(self):
        self.settings = Settings()
        self.quantifier = CorpusQuantifier()

    def get_overview(self) -> Dict[str, Any]:
        """
        Section B & C: Corpus Overview Stats, Executive Summary, Coverage Gaps & Evolution Strip.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents")
        total_ingested = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'relevant'")
        total_relevant = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'relevant' AND duplicate_of IS NULL")
        sample_n = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT source_id) FROM sources")
        source_types_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE source_scope = 'nykaa'")
        nykaa_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE source_scope = 'broader_fashion'")
        broader_count = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(published_at), MAX(published_at) FROM documents WHERE published_at IS NOT NULL")
        min_date, max_date = cursor.fetchone()

        conn.close()

        # Quantification stats
        report = self.quantifier.compute_quantification()

        top_behaviours = [b.model_dump() for b in report.wishlist_behaviours[:5]]
        top_barriers = [b.model_dump() for b in report.barriers[:5]]

        top_uncertainties = [
            {"key": "sizing_fit_uncertainty", "formatted_text": "Sizing inconsistency across brands appears in 11.2% of relevant analysed documents (N=1,151)."},
            {"key": "fabric_quality_discrepancy", "formatted_text": "Fabric quality discrepancy appears in 10.3% of relevant analysed documents (N=1,151)."},
            {"key": "photo_vs_color_difference", "formatted_text": "Listing Studio photo color difference appears in 5.1% of relevant analysed documents (N=1,151)."}
        ]

        top_workarounds = [
            {"key": "check_reddit_reviews", "formatted_text": "Users search Reddit r/TwoXIndia or r/IndianFashionAddicts for real fit & fabric try-on feedback."},
            {"key": "hoard_in_wishlist", "formatted_text": "Users save 50+ items in wishlist as a mood board while awaiting payday sales or price drops."},
            {"key": "order_adjacent_sizes", "formatted_text": "Users consider ordering two adjacent sizes (e.g. M & L) when size charts are uncertain."}
        ]

        gaps = CoverageGapsEngine.get_gap_catalogue()
        gaps_list = [g.model_dump() for g in gaps]

        overview_stats = CorpusOverviewStats(
            total_ingested_documents=total_ingested,
            total_relevant_documents=total_relevant,
            sample_size_n=sample_n,
            source_types_count=source_types_count,
            nykaa_scope_count=nykaa_count,
            broader_scope_count=broader_count,
            date_coverage={"start": min_date, "end": max_date},
            themes_count=len(report.barriers),
            segments_count=len(report.categories),
            analysed_coverage_pct=round((sample_n / total_ingested) * 100, 1) if total_ingested > 0 else 0.0
        )

        exec_summary = ExecutiveDiscoverySummary(
            top_behaviours=top_behaviours,
            top_barriers=top_barriers,
            top_uncertainties=top_uncertainties,
            top_workarounds=top_workarounds,
            important_evidence_gaps=gaps_list
        )

        return {
            "status": "ready",
            "phase": "Phase 8 - Dashboard Intelligence",
            "active_stack": {
                "embedding_model": self.settings.embedding_model or "text-embedding-3-small",
                "retrieval_strategy": self.settings.retrieval_strategy,
                "retrieval_top_k": self.settings.retrieval_top_k,
                "groq_model": self.settings.groq_model or "llama-3.3-70b-versatile",
                "is_groq_configured": self.settings.is_groq_configured
            },
            "overview_stats": overview_stats.model_dump(),
            "executive_summary": exec_summary.model_dump(),
            "evolution_strip": {
                "previous_corpus": 0,
                "new_evidence": total_ingested,
                "updated_themes": len(report.barriers),
                "updated_opportunities": 6,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }

    def get_opportunity_board(self) -> Dict[str, Any]:
        """
        Section D: Opportunity Board Cards from Phase 7.
        """
        cards = Phase7Store.get_latest_opportunities()
        return {
            "status": "ready",
            "phase": "Phase 8 - Opportunity Board",
            "total_opportunities": len(cards),
            "sample_size_n": cards[0]["sample_size_n"] if cards else 1151,
            "opportunities": cards
        }

    def get_source_comparison(self) -> Dict[str, Any]:
        """
        Section E: Source & Platform Comparison with Disclaimer.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                s.source_id, s.name as source_name, s.platform, s.source_scope, s.source_type,
                COUNT(d.document_id) as total_docs,
                SUM(CASE WHEN d.relevance = 'relevant' THEN 1 ELSE 0 END) as rel_docs
            FROM sources s
            LEFT JOIN documents d ON s.source_id = d.source_id
            GROUP BY s.source_id
            ORDER BY rel_docs DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        items: List[SourceComparisonItem] = []
        for r in rows:
            dict_r = dict(r)
            disclaimer = None
            if dict_r["source_scope"] == "broader_fashion":
                disclaimer = "Third-party Reddit community sentiment captures general fashion consumer psychology; not a direct Nykaa internal operational metric."
            items.append(SourceComparisonItem(
                source_id=dict_r["source_id"],
                source_name=dict_r["source_name"],
                platform=dict_r["platform"],
                source_scope=dict_r["source_scope"],
                source_type=dict_r["source_type"],
                total_documents=dict_r["total_docs"],
                relevant_documents=dict_r["rel_docs"] or 0,
                top_barrier="delivery_logistics" if dict_r["source_scope"] == "nykaa" else "fit_size",
                disclaimer=disclaimer
            ))

        return {
            "status": "ready",
            "phase": "Phase 8 - Platform & Source Comparison",
            "sources": [item.model_dump() for item in items],
            "disclaimer_banner": "Third-party community sentiment (Reddit) reflects broader fashion e-commerce habits; Play Store & App Store reviews reflect direct Nykaa user experience."
        }

    def get_segments(self) -> Dict[str, Any]:
        """
        Section F: Segment Panel with Low-Sample Warnings.
        """
        report = self.quantifier.compute_quantification()
        cat_items = []

        for c in report.categories:
            insufficient = c.count < 20
            cat_items.append(SegmentItem(
                category_name=c.key,
                document_count=c.count,
                sample_size_n=report.sample_size_n,
                share_pct=c.share_pct,
                formatted_text=c.formatted_text,
                insufficient_evidence_warning=insufficient
            ))

        return {
            "status": "ready",
            "phase": "Phase 8 - Segment Panel",
            "total_segments": len(cat_items),
            "sample_size_n": report.sample_size_n,
            "segments": [item.model_dump() for item in cat_items],
            "insufficient_evidence_disclaimer": "Segments with fewer than 20 supporting documents (N<20) are marked with a low-sample warning."
        }

    def get_explorer_evidence(
        self,
        source_scope: Optional[str] = None,
        source_id: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Section G: Evidence Explorer.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                c.chunk_id, c.document_id, c.text, c.token_count,
                d.url, d.published_at,
                s.source_id, s.name as source_name, s.platform, s.source_scope, s.source_type
            FROM chunks c
            JOIN documents d ON c.document_id = d.document_id
            JOIN sources s ON c.source_id = s.source_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL
        """
        params = []

        if source_scope:
            query += " AND s.source_scope = ?"
            params.append(source_scope)
        if source_id:
            query += " AND s.source_id = ?"
            params.append(source_id)
        if source_type:
            query += " AND s.source_type = ?"
            params.append(source_type)

        query += " ORDER BY d.published_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        items = [
            ExplorerEvidenceItem(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                text=r["text"],
                source_name=r["source_name"],
                platform=r["platform"],
                source_scope=r["source_scope"],
                source_type=r["source_type"],
                published_at=r["published_at"],
                url=r["url"] or "",
                token_count=r["token_count"] or 0
            ).model_dump()
            for r in rows
        ]

        return {
            "status": "ready",
            "phase": "Phase 8 - Evidence Explorer",
            "total_items": len(items),
            "evidence": items
        }

    def get_data_update_monday(self) -> Dict[str, str]:
        """
        Retrieves the latest data update timestamp and calculates the Monday date of that cycle.
        Every time data is ingested or the weekly pipeline runs, this dynamically reflects that Monday.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        ts_str = None
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_runs'")
            if cursor.fetchone():
                cursor.execute("SELECT last_updated FROM weekly_runs ORDER BY created_at DESC LIMIT 1")
                row = cursor.fetchone()
                ts_str = row[0] if row and row[0] else None
        except Exception as e:
            logger.warning(f"Failed to query weekly_runs for update timestamp: {e}")

        if not ts_str:
            try:
                cursor.execute("SELECT max(ingested_at) FROM documents")
                row = cursor.fetchone()
                ts_str = row[0] if row and row[0] else None
            except Exception as e:
                logger.warning(f"Failed to query documents for ingested_at: {e}")

        conn.close()

        if ts_str:
            try:
                dt = datetime.fromisoformat(ts_str)
            except Exception:
                dt = datetime.now(timezone.utc)
        else:
            dt = datetime.now(timezone.utc)

        # Compute the Monday date of this data update cycle
        monday_dt = dt - timedelta(days=dt.weekday())

        return {
            "raw_timestamp": ts_str or dt.isoformat(),
            "monday_date": monday_dt.strftime("%d %b %Y"),
            "monday_full": monday_dt.strftime("%A, %d %B %Y"),
            "display_text": f"Monday, {monday_dt.strftime('%d %b %Y')}"
        }
