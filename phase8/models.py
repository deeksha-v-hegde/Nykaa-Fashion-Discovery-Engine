from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CorpusOverviewStats(BaseModel):
    total_ingested_documents: int
    total_relevant_documents: int
    sample_size_n: int = 1151
    source_types_count: int
    nykaa_scope_count: int
    broader_scope_count: int
    date_coverage: Dict[str, Optional[str]]
    themes_count: int
    segments_count: int
    analysed_coverage_pct: float


class ExecutiveDiscoverySummary(BaseModel):
    top_behaviours: List[Dict[str, Any]]
    top_barriers: List[Dict[str, Any]]
    top_uncertainties: List[Dict[str, Any]]
    top_workarounds: List[Dict[str, Any]]
    important_evidence_gaps: List[Dict[str, Any]]


class SourceComparisonItem(BaseModel):
    source_id: str
    source_name: str
    platform: str
    source_scope: str
    source_type: str
    total_documents: int
    relevant_documents: int
    top_barrier: str
    disclaimer: Optional[str] = None


class SegmentItem(BaseModel):
    category_name: str
    document_count: int
    sample_size_n: int = 1151
    share_pct: float
    formatted_text: str
    insufficient_evidence_warning: bool = False


class ExplorerEvidenceItem(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    source_name: str
    platform: str
    source_scope: str
    source_type: str
    published_at: Optional[str] = None
    url: str
    token_count: int


class CitationDetailPayload(BaseModel):
    chunk_id: str
    document_id: str
    source_id: str
    source_name: str
    platform: str
    source_scope: str
    source_type: str
    published_at: Optional[str] = None
    url: str
    chunk_text: str
    cleaned_text: str
    raw_text: str
    relevance: str
    duplicate_of: Optional[str] = None
