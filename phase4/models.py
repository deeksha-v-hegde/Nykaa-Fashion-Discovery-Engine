from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Structured evidence item citing a specific retrieved chunk."""
    chunk_id: str
    document_id: str
    snippet: str
    source_id: str
    source_name: str
    platform: str
    source_type: str
    source_scope: str
    published_at: Optional[str] = None
    url: str
    retrieval_relevance: float


class MetricConnection(BaseModel):
    """
    Grounded mapping of the discovery finding to the 30-day wishlist-to-purchase journey.
    Each hop is strictly marked observed, inferred, or unknown.
    """
    wishlist_to_reconsideration: Literal["observed", "inferred", "unknown"] = "observed"
    reconsideration_to_confidence: Literal["observed", "inferred", "unknown"] = "inferred"
    confidence_to_cart: Literal["observed", "inferred", "unknown"] = "inferred"
    cart_to_purchase: Literal["observed", "inferred", "unknown"] = "inferred"
    thirty_day_conversion: Literal["observed", "inferred", "unknown"] = "unknown"
    explanation: str


class ConflictInfo(BaseModel):
    """Represents divergent or conflicting viewpoints in the evidence."""
    detected: bool = False
    viewpoint_a: Optional[str] = None
    viewpoint_b: Optional[str] = None
    recommendation: Optional[str] = None


class DiscoveryResponse(BaseModel):
    """
    Master Structured Discovery Output from Phase 4 Grounded RAG.
    Strictly adheres to Phase 4 JSON contract.
    """
    query: str
    grounded_answer: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    pattern: str
    inference: str
    confidence: Literal["High", "Medium", "Low"]
    confidence_reason: str
    evidence_gap: str
    metric_connection: MetricConnection
    related_opportunity_ids: List[str] = Field(default_factory=list)
    nykaa_evidence_limited: bool = False
    disclaimer_text: Optional[str] = None
    conflict: Optional[ConflictInfo] = None
    status: Literal["success", "refusal", "insufficient_evidence", "error"] = "success"
    error_message: Optional[str] = None
    trace_id: Optional[str] = None


class QueryTraceRecord(BaseModel):
    """Execution trace record for query auditing and citation inspection."""
    trace_id: str
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    retrieved_chunk_ids: List[str] = Field(default_factory=list)
    top_score: float = 0.0
    status: str
    nykaa_evidence_limited: bool = False
    latency_ms: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
