import logging
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from phase7.pipeline import OpportunityPipeline
from phase7.store import Phase7Store

logger = logging.getLogger("nykaa_engine.api_opps")
router = APIRouter(prefix="/api/opportunities", tags=["Phase 7: Prioritised Opportunities"])

pipeline = OpportunityPipeline()


@router.get("", response_model=Dict[str, Any])
def get_opportunities() -> Dict[str, Any]:
    """
    Returns the Prioritised Research Shortlist of ranked opportunities.
    Includes 6-factor weighted scores, citations, metric journey hops, and scale (N=1,151).
    Rank 1 is strictly labeled 'Recommended opportunity to validate'.
    """
    try:
        cards = Phase7Store.get_latest_opportunities()
        if not cards:
            card_models = pipeline.run_pipeline()
            cards = [c.model_dump() for c in card_models]

        return {
            "status": "ready",
            "phase": "Phase 7 - Opportunities & Metric Journey",
            "total_opportunities": len(cards),
            "sample_size_n": cards[0]["sample_size_n"] if cards else 1151,
            "opportunities": cards
        }
    except Exception as e:
        logger.error(f"Opportunities API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{opportunity_id}", response_model=Dict[str, Any])
def get_opportunity_detail(opportunity_id: str) -> Dict[str, Any]:
    """
    Returns full detail payload for a specific opportunity card (for Explore Evidence drawer).
    """
    try:
        card = Phase7Store.get_opportunity_by_id(opportunity_id)
        if not card:
            raise HTTPException(status_code=404, detail=f"Opportunity '{opportunity_id}' not found.")

        return {
            "status": "success",
            "opportunity": card
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Opportunity detail API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
