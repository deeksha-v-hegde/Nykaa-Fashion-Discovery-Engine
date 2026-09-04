from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class SourceStatusItem(BaseModel):
    source_id: str
    name: str
    platform: str
    source_scope: str
    source_type: str
    status: Literal["active", "partial", "error", "manual_unavailable"]
    total_ingested: int = 0
    relevant_ingested: int = 0
    last_fetched_at: Optional[str] = None
    error_message: Optional[str] = None


class CorpusEvolutionDiff(BaseModel):
    previous_corpus_count: int
    new_evidence_count: int
    updated_themes_count: int
    updated_opportunities_count: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConflictResult(BaseModel):
    conflict_detected: bool = False
    topic: str
    viewpoint_a: Optional[str] = None
    viewpoint_b: Optional[str] = None
    disclaimer: str = "Conflicting evidence detected. Additional primary research is required to resolve divergent user feedback."
    evidence_chunk_ids: List[str] = Field(default_factory=list)


class WeeklyRunRecord(BaseModel):
    run_id: str
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    next_scheduled_run: str
    new_documents_this_week: int
    new_relevant_documents: int
    sources_successful_count: int
    sources_failed_count: int
    sources_total_count: int
    analysis_status: Literal["success", "partial", "failed"]
    per_source_results: Dict[str, Any] = Field(default_factory=dict)
    processing_errors: List[str] = Field(default_factory=list)
    last_successful_run: Optional[str] = None
    evolution_diff: CorpusEvolutionDiff
