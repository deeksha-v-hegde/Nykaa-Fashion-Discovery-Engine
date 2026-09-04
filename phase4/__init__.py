"""
Phase 4: Grounded RAG Discovery Engine.
"""

from phase4.models import (
    EvidenceItem,
    MetricConnection,
    ConflictInfo,
    DiscoveryResponse,
    QueryTraceRecord
)
from phase4.monetary_detector import MonetaryDetector, REFUSAL_MESSAGE
from phase4.query_processor import QueryProcessor
from phase4.grounding_validator import GroundingValidator
from phase4.confidence_scorer import ConfidenceScorer
from phase4.store import Phase4Store, init_phase4_schema
from phase4.ask_engine import AskEngine

__all__ = [
    "EvidenceItem",
    "MetricConnection",
    "ConflictInfo",
    "DiscoveryResponse",
    "QueryTraceRecord",
    "MonetaryDetector",
    "REFUSAL_MESSAGE",
    "QueryProcessor",
    "GroundingValidator",
    "ConfidenceScorer",
    "Phase4Store",
    "init_phase4_schema",
    "AskEngine"
]
