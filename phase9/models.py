from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from phase4.models import EvidenceItem


class PresetQuestionItem(BaseModel):
    preset_id: str
    prompt: str
    category: str
    evidence_strength: Literal["strong", "moderate", "weak"]
    evidence_strength_badge: str
    coverage_note: str
    default_filters: Dict[str, Any] = Field(default_factory=dict)


class FollowUpChipItem(BaseModel):
    chip_id: str
    label: str
    action_type: str
    query_template: str


class GroundedAskSectionPayload(BaseModel):
    grounded_answer: str
    evidence_passages: List[EvidenceItem] = Field(default_factory=list)
    pattern_summary: str
    inference_narrative: str
    confidence_rating: Literal["High", "Medium", "Low"]
    confidence_rationale: str
    evidence_gap: str
    metric_connection: str
    related_opportunity_ids: List[str] = Field(default_factory=list)
    related_opportunity_titles: List[str] = Field(default_factory=list)
    suggested_followups: List[FollowUpChipItem] = Field(default_factory=list)


class AskSessionState(BaseModel):
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
