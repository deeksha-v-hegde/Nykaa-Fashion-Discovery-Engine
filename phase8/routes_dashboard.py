import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from phase8.citation_inspector import CitationInspector
from phase8.dashboard_service import DashboardService

logger = logging.getLogger("nykaa_engine.api_dashboard")
router = APIRouter(prefix="/api/dashboard", tags=["Phase 8: PM Dashboard Intelligence"])

dash_service = DashboardService()


@router.get("/overview")
def get_dashboard_overview() -> Dict[str, Any]:
    """
    Section B & C: Corpus Overview, Executive Discovery Summary, Coverage Gaps & Evolution Strip.
    """
    try:
        return dash_service.get_overview()
    except Exception as e:
        logger.error(f"Overview API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/board")
def get_dashboard_board() -> Dict[str, Any]:
    """
    Section D: Opportunity Board Cards from Phase 7.
    Rank 1 labeled 'Recommended opportunity to validate'.
    """
    try:
        return dash_service.get_opportunity_board()
    except Exception as e:
        logger.error(f"Board API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
def get_dashboard_comparison() -> Dict[str, Any]:
    """
    Section E: Platform & Source Comparison Filters (Nykaa Scope vs Broader Fashion).
    """
    try:
        return dash_service.get_source_comparison()
    except Exception as e:
        logger.error(f"Comparison API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments")
def get_dashboard_segments() -> Dict[str, Any]:
    """
    Section F: Segment Panel with Low-Sample Warnings (N<20).
    """
    try:
        return dash_service.get_segments()
    except Exception as e:
        logger.error(f"Segments API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explorer")
def get_dashboard_explorer(
    source_scope: Optional[str] = Query(default=None, description="Filter by 'nykaa' or 'broader_fashion'"),
    source_id: Optional[str] = Query(default=None, description="Filter by source_id"),
    source_type: Optional[str] = Query(default=None, description="Filter by 'app_reviews' or 'community_discussion'"),
    limit: int = Query(default=50, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Section G: Evidence Explorer for raw chunk browsing.
    """
    try:
        return dash_service.get_explorer_evidence(
            source_scope=source_scope,
            source_id=source_id,
            source_type=source_type,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Explorer API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/citations/{chunk_id}")
def get_citation_detail(chunk_id: str) -> Dict[str, Any]:
    """
    Citation Inspector: Resolves chunk_id to its full raw source provenance chain.
    """
    try:
        detail = CitationInspector.get_citation_detail(chunk_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Citation for chunk_id '{chunk_id}' not found.")

        return {
            "status": "success",
            "citation": detail.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Citation Inspector API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
