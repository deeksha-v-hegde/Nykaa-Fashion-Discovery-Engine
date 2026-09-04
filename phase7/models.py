from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class MetricJourneyHops(BaseModel):
    """
    Visualization hops for the 30-day wishlist-to-purchase metric journey.
    Hop 5 (30-day conversion) is strictly unknown due to lack of longitudinal UGC tracking.
    """
    wishlist_added: Literal["observed", "inferred", "unknown"] = "observed"
    reconsideration: Literal["observed", "inferred", "unknown"] = "observed"
    confidence_building: Literal["observed", "inferred", "unknown"] = "inferred"
    cart_addition: Literal["observed", "inferred", "unknown"] = "inferred"
    purchase_completion_30day: Literal["observed", "inferred", "unknown"] = "unknown"
    journey_narrative: str


class ScoringBreakdown(BaseModel):
    """6-Factor weighted prioritisation score breakdown."""
    score_frequency: float = Field(..., ge=1.0, le=5.0, description="Corpus frequency scale (1-5)")
    score_metric_relevance: float = Field(..., ge=1.0, le=5.0, description="Friction impact on conversion (1-5)")
    score_pain: float = Field(..., ge=1.0, le=5.0, description="User pain & frustration severity (1-5)")
    score_evidence: float = Field(..., ge=1.0, le=5.0, description="Evidence quality & strength (1-5)")
    score_cross_source: float = Field(..., ge=1.0, le=5.0, description="Cross-platform presence (1-5)")
    score_solvability: float = Field(..., ge=1.0, le=5.0, description="Non-monetary AI/Product solvability (1-5)")
    research_prioritisation_score: float = Field(..., ge=1.0, le=5.0, description="Weighted composite score")
    weights_used: Dict[str, float] = Field(default_factory=dict)


class OpportunityCitation(BaseModel):
    """Verbatim citation linking opportunity to raw source chunk."""
    chunk_id: str
    document_id: str
    snippet: str
    source_name: str
    source_scope: str
    published_at: Optional[str] = None
    url: str


class OpportunityCard(BaseModel):
    """
    Master Opportunity Card contract for the Prioritised Research Shortlist.
    """
    opportunity_id: str
    rank: int
    title: str
    rank_label: str
    status: Literal["validate_next", "under_investigation", "validated"] = "validate_next"
    user_job: str
    blocker: str
    current_workaround: str
    non_monetary_intervention_type: str
    scale_mention_count: int
    scale_share_pct: float
    sample_size_n: int = 1025
    scale_formatted: str
    confidence: Literal["High", "Medium", "Low"]
    evidence_gap: str
    research_hypothesis: str
    journey: MetricJourneyHops
    scoring: ScoringBreakdown
    citations: List[OpportunityCitation] = Field(default_factory=list)
    snapshot_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    direct_wishlist_count: int = 0
    funnel_stage: str = "Pre-Purchase / Reconsideration"
    signal_type: str = "primary_wishlist"
    compounding_notes: Optional[str] = None
