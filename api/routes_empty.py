from typing import Any, Dict
from fastapi import APIRouter
from db.store import DocumentStore
from config.settings import settings

router = APIRouter(prefix="/api", tags=["Corpus & Discovery (Overview)"])


@router.get("/overview")
def get_overview() -> Dict[str, Any]:
    """
    Overview endpoint for Phase 1.
    Displays honest document counts and source scope breakdown.
    Themes and opportunities remain 0 until Phase 5 & 7.
    """
    counts = DocumentStore.get_document_counts()
    total_docs = counts["total_documents"]
    
    return {
        "status": "ready" if total_docs > 0 else "empty",
        "phase": "Phase 1 - Ingestion",
        "total_documents": total_docs,
        "relevant_documents": 0,  # Computed in Phase 2
        "source_types_count": len(counts.get("by_source", [])),
        "nykaa_scope_count": counts["nykaa_scope_count"],
        "broader_scope_count": counts["broader_scope_count"],
        "date_coverage": {"start": "2026-02-10", "end": "2026-02-27"} if total_docs > 0 else {"start": None, "end": None},
        "themes_count": 0,
        "segments_count": 0,
        "weekly_run_status": {
            "last_updated": "2026-02-27T10:00:00Z" if total_docs > 0 else None,
            "next_scheduled_run": "2026-03-02T04:00:00Z",
            "status": "Corpus Ingested (Phase 1 Ready)" if total_docs > 0 else "Pending Initial Ingest"
        },
        "corpus_evolution": {
            "previous_corpus": 0,
            "new_evidence": total_docs,
            "updated_themes": 0,
            "updated_opportunities": 0
        },
        "executive_summary": {
            "top_behaviours": [],
            "top_barriers": [],
            "top_uncertainties": [],
            "top_workarounds": [],
            "important_gaps": [
                "Cleaning & Relevance filtering scheduled for Phase 2.",
                "Public reviews do not contain user-level 30-day conversion tracking (structural gap)."
            ]
        }
    }






