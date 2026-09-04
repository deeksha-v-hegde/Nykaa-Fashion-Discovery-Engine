from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, HTTPException

from db.store import DocumentStore
from phase1.store import Phase1DocumentStore
from phase2.pipeline import Phase2Pipeline
from phase2.store import Phase2Store

router = APIRouter(prefix="/api/corpus", tags=["Corpus & Discovery Engine (Phase 1 & 2)"])


@router.post("/ingest")
def trigger_ingestion() -> Dict[str, Any]:
    """
    Triggers Phase 1 ingestion job across registered public sources.
    Performs SHA-256 hash deduplication and stores raw documents.
    """
    try:
        from phase1.ingest import Phase1IngestionJob
        job = Phase1IngestionJob()
        result = job.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion job failed: {str(e)}")


@router.post("/clean")
def trigger_cleaning() -> Dict[str, Any]:
    """
    Triggers Phase 2 text normalization, near-duplicate detection,
    domain relevance classification, and sentence-aware chunking.
    """
    try:
        pipeline = Phase2Pipeline()
        result = pipeline.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleaning pipeline failed: {str(e)}")


@router.get("/stats")
def get_corpus_stats() -> Dict[str, Any]:
    """
    Returns unified Phase 1 and Phase 2 statistics:
    - Raw document counts by scope & source
    - Phase 2 relevance breakdown (relevant, not_relevant, unknown)
    - Total chunks and token counts
    """
    phase1_stats = Phase1DocumentStore.get_stats()
    phase2_stats = Phase2Store.get_phase2_stats()
    return {
        "phase1": phase1_stats,
        "phase2": phase2_stats
    }


@router.get("/documents")
def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source_scope: Optional[str] = Query(default=None, pattern="^(nykaa|broader_fashion)$"),
    source_id: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lists ingested raw documents with provenance metadata, pagination, and filtering.
    """
    return Phase1DocumentStore.list_documents(
        limit=limit,
        offset=offset,
        source_scope=source_scope,
        source_id=source_id,
        search_query=search
    )
