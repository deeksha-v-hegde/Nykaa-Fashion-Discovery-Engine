from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthCheckResult(BaseModel):
    component: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ChaosTestResult(BaseModel):
    test_name: str
    simulated_failure: str
    expected_fallback: str
    actual_outcome: str
    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class SystemHardeningReport(BaseModel):
    groq_outage_fallback_passed: bool
    monetary_interception_passed: bool
    weak_evidence_disclosure_passed: bool
    rate_limit_backoff_passed: bool
    overall_health: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
