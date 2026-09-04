import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from phase4.ask_engine import AskEngine
from phase4.models import DiscoveryResponse
from phase4.store import Phase4Store
from phase9.ask_session_service import AskSessionService
from phase9.presets_catalogue import PresetsCatalogue

logger = logging.getLogger("nykaa_engine.api_ask")
router = APIRouter(prefix="/api/ask", tags=["Phase 4 & 9: Grounded Ask Engine UI"])

ask_engine = AskEngine()
session_service = AskSessionService()


class AskRequestPayload(BaseModel):
    query: str = Field(..., description="User discovery question")
    session_id: Optional[str] = Field(default=None)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata filters")
    source_scope: Optional[str] = Field(default=None)
    source_type: Optional[str] = Field(default=None)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)


@router.get("/presets")
def get_presets() -> Dict[str, Any]:
    """
    Phase 9: Returns the 10 official one-click research presets with evidence strength badges.
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


@router.post("", response_model=DiscoveryResponse)
async def ask_discovery(request: AskRequestPayload):
    """
    Phase 4: Execute grounded RAG discovery query.
    """
    try:
        response = ask_engine.ask(
            query=request.query,
            filters=request.filters,
            top_k=request.top_k
        )
        return response
    except Exception as e:
        logger.error(f"Ask API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal discovery engine error: {str(e)}")


@router.post("/query")
def post_structured_query(payload: AskRequestPayload) -> Dict[str, Any]:
    """
    Phase 9: Executes grounded RAG query and returns 9 distinct structured response sections.
    """
    try:
        filters = payload.filters or {}
        if payload.source_scope:
            filters["source_scope"] = payload.source_scope
        if payload.source_type:
            filters["source_type"] = payload.source_type
        filters["top_k"] = payload.top_k or 5

        return session_service.execute_ask_query(
            query=payload.query,
            session_id=payload.session_id,
            filters=filters
        )
    except Exception as e:
        logger.error(f"Structured Ask API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/follow-up")
def post_followup(payload: AskRequestPayload) -> Dict[str, Any]:
    """
    Phase 9: Executes follow-up query inheriting active session filters.
    """
    try:
        return session_service.execute_ask_query(
            query=payload.query,
            session_id=payload.session_id
        )
    except Exception as e:
        logger.error(f"Ask follow-up API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces")
async def get_query_traces(limit: int = Query(default=20, ge=1, le=100)):
    """
    Returns recent Phase 4 query execution traces.
    """
    try:
        traces = Phase4Store.get_traces(limit=limit)
        return {"total": len(traces), "traces": traces}
    except Exception as e:
        logger.error(f"Error fetching traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))
