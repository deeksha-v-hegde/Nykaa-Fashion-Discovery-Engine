import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

from phase10.conflict_resolver import ConflictResolver
from phase10.source_registry import SourceRegistry
from phase10.store import Phase10Store
from phase10.weekly_pipeline import WeeklyPipeline

logger = logging.getLogger("nykaa_engine.api_weekly")
router = APIRouter(prefix="/api/weekly", tags=["Phase 10: Weekly Research System"])

weekly_pipeline = WeeklyPipeline()


@router.get("/status")
def get_weekly_status() -> Dict[str, Any]:
    """
    Returns latest WeeklyRun record, source status registers, and conflict report.
    """
    try:
        latest_run = Phase10Store.get_latest_weekly_run()
        if not latest_run:
            record = weekly_pipeline.run_weekly_pipeline()
            latest_run = record.model_dump()

        sources = SourceRegistry.get_registered_sources()
        conflict = ConflictResolver.detect_conflicts(
            query="fit size delivery return",
            evidence_texts=[]
        )

        return {
            "status": "ready",
            "phase": "Phase 10 - Weekly Research System",
            "latest_run": latest_run,
            "registered_sources": [s.model_dump() for s in sources],
            "conflict_status": conflict.model_dump()
        }
    except Exception as e:
        logger.error(f"Weekly Status API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
def trigger_weekly_run() -> Dict[str, Any]:
    """
    Triggers incremental Monday research pipeline pass.
    """
    try:
        record = weekly_pipeline.run_weekly_pipeline()
        return {
            "status": "success",
            "message": "Weekly incremental research pipeline executed successfully.",
            "weekly_run": record.model_dump()
        }
    except Exception as e:
        logger.error(f"Weekly Pipeline Trigger error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
