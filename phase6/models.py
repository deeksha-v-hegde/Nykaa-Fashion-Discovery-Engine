from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StatItem(BaseModel):
    key: str
    count: int
    sample_size_n: int
    share_pct: float
    formatted_text: str
    cross_source_consistency: int = 1
    source_types: List[str] = Field(default_factory=list)


class ScopeDistribution(BaseModel):
    nykaa_count: int
    nykaa_share_pct: float
    broader_count: int
    broader_share_pct: float
    total_n: int
    formatted_text: str


class QuantificationReport(BaseModel):
    snapshot_id: str
    sample_size_n: int
    barriers: List[StatItem]
    wishlist_behaviours: List[StatItem]
    categories: List[StatItem]
    scope_distribution: ScopeDistribution
    evidence_strengths: Dict[str, int]
    emerging_themes_count: int
    computed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CoverageGapItem(BaseModel):
    gap_id: str
    category: str  # "Structural Gap", "Corpus Gap", or "Emerging Theme"
    title: str
    description: str
    impact: str
    recommended_action: str
    status: str = "Active"
