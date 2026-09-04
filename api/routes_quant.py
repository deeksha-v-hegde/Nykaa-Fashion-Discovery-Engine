import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

from phase6.coverage_gaps import CoverageGapsEngine
from phase6.quantifier import CorpusQuantifier
from phase6.store import Phase6Store

logger = logging.getLogger("nykaa_engine.api_quant")
router = APIRouter(prefix="/api", tags=["Phase 6: Quantification & Coverage Gaps"])

quantifier = CorpusQuantifier()


@router.get("/quantification")
def get_quantification() -> Dict[str, Any]:
    """
    Returns denominator-bearing statistics over canonical relevant documents (N=1,151).
    Strictly forbids population claims and enforces explicit (N=count) templates.
    """
    try:
        snapshot = Phase6Store.get_latest_snapshot()
        if not snapshot:
            report = quantifier.compute_quantification()
            sid = Phase6Store.save_snapshot(report.sample_size_n, report.model_dump())
            report.snapshot_id = sid
            report_dict = report.model_dump()
        else:
            report_dict = snapshot["report"]

        return {
            "status": "success",
            "phase": "Phase 6 - Quantification",
            "quantification": report_dict
        }
    except Exception as e:
        logger.error(f"Quantification API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage-gaps")
def get_coverage_gaps() -> Dict[str, Any]:
    """
    Returns structural data gaps (30-day conversion gap, monetary exclusion)
    and corpus coverage statistics.
    """
    try:
        gaps = CoverageGapsEngine.get_gap_catalogue()
        coverage = CoverageGapsEngine.compute_corpus_coverage()

        return {
            "status": "success",
            "phase": "Phase 6 - Coverage & Gaps",
            "coverage": coverage,
            "structural_gaps": [g.model_dump() for g in gaps]
        }
    except Exception as e:
        logger.error(f"Coverage Gaps API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
