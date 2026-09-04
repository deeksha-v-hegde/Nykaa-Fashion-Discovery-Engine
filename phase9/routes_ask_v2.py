import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from phase9.ask_session_service import AskSessionService
from phase9.presets_catalogue import PresetsCatalogue

logger = logging.getLogger("nykaa_engine.api_ask_v2")
router = APIRouter(prefix="/api/ask", tags=["Phase 9: Ask Engine UI"])

session_service = AskSessionService()


class QueryPayload(BaseModel):
    query: str
    session_id: Optional[str] = None
    source_scope: Optional[str] = None
    source_type: Optional[str] = None
    top_k: int = 5


@router.get("/presets")
def get_presets() -> Dict[str, Any]:
    """
    Returns the 10 official one-click research presets with evidence strength badges.
    """
    try:
        presets = PresetsCatalogue.get_presets()
        chips = PresetsCatalogue.get_followup_chips()
        return {
            "status": "ready",
            "phase": "Phase 9 - Ask Engine Presets",
            "total_presets": len(presets),
            "presets": [p.model_dump() for p in presets],
            "followup_chips": [c.model_dump() for c in chips]
        }
    except Exception as e:
        logger.error(f"Presets API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
def post_query(payload: QueryPayload) -> Dict[str, Any]:
    """
    Executes a grounded RAG query and returns 9 distinct structured response sections.
    """
    try:
        filters = {}
        if payload.source_scope:
            filters["source_scope"] = payload.source_scope
        if payload.source_type:
            filters["source_type"] = payload.source_type
        filters["top_k"] = payload.top_k

        return session_service.execute_ask_query(
            query=payload.query,
            session_id=payload.session_id,
            filters=filters
        )
    except Exception as e:
        logger.error(f"Ask query API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/follow-up")
def post_followup(payload: QueryPayload) -> Dict[str, Any]:
    """
    Executes a follow-up query inheriting active session filters.
    """
    try:
        return session_service.execute_ask_query(
            query=payload.query,
            session_id=payload.session_id
        )
    except Exception as e:
        logger.error(f"Ask follow-up API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
