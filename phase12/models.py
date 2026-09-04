from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DeploymentCheckResult(BaseModel):
    check_name: str
    category: str
    status: Literal["PASS", "FAIL", "WARNING"]
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class DeploymentVerificationReport(BaseModel):
    deployment_ready: bool
    entrypoint: str = "phase11/app.py"
    db_path: str = "data/discovery_engine.db"
    vector_store_path: str = "data/vector_store/lsa_embedder_v1.joblib"
    total_checks_passed: int
    total_checks_failed: int
    checks: List[DeploymentCheckResult] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
