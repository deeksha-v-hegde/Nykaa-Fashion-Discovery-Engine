from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DocumentExtraction(BaseModel):
    """
    Phase 5 Structured Document Extraction Schema.
    Strictly enforces Null-If-Unsupported policy for unsupported fields.
    """
    document_id: str
    product_category: Optional[str] = Field(default=None, description="Apparel category (e.g. Kurta, Dress, Jeans, Footwear)")
    user_behaviour: Optional[str] = Field(default=None, description="Observed user action or shopping habit")
    wishlist_behaviour: Optional[str] = Field(default=None, description="Taxonomy classification of wishlist usage")
    purchase_intent: Optional[str] = Field(default=None, description="Explicit purchase intent indicator")
    purchase_stage: Optional[str] = Field(default=None, description="Stage in purchase funnel (e.g. Discovery, Consideration, Decision)")
    barrier: Optional[str] = Field(default=None, description="Primary purchase barrier taxonomy key")
    uncertainty: Optional[str] = Field(default=None, description="Specific doubt or risk causing hesitation")
    user_job: Optional[str] = Field(default=None, description="User's underlying functional or emotional goal")
    workaround: Optional[str] = Field(default=None, description="Compensating action taken by user (e.g. ordering 2 sizes)")
    external_information_source: Optional[str] = Field(default=None, description="External site checked (e.g. Reddit, YouTube, Instagram)")
    alternative_considered: Optional[str] = Field(default=None, description="Competitor platform or alternative brand")
    occasion: Optional[str] = Field(default=None, description="Target event or occasion (e.g. Wedding, Office, Festive)")
    fit_size: Optional[str] = Field(default=None, description="Specific sizing/fit observation or complaint")
    styling: Optional[str] = Field(default=None, description="Styling or outfit pairing detail")
    price: Optional[str] = Field(default=None, description="Price perception or budget timing note")
    reviews_social_validation: Optional[str] = Field(default=None, description="Review or social proof mention")
    availability: Optional[str] = Field(default=None, description="Stock or size availability detail")
    quality_expectation: Optional[str] = Field(default=None, description="Fabric, material, or quality feedback")
    other_new_theme: Optional[str] = Field(default=None, description="Novel or emerging theme not in seed taxonomy")
    evidence_strength: Literal["high", "medium", "low"] = Field(default="medium", description="Explicit evidence strength in source document")
    extracted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return self.model_dump()
