"""
Phase 8: Dashboard Intelligence Service (Overview, Board, Explorer, Citations).
"""

from phase8.models import (
    CorpusOverviewStats,
    ExecutiveDiscoverySummary,
    SourceComparisonItem,
    SegmentItem,
    ExplorerEvidenceItem,
    CitationDetailPayload
)
from phase8.citation_inspector import CitationInspector
from phase8.dashboard_service import DashboardService

__all__ = [
    "CorpusOverviewStats",
    "ExecutiveDiscoverySummary",
    "SourceComparisonItem",
    "SegmentItem",
    "ExplorerEvidenceItem",
    "CitationDetailPayload",
    "CitationInspector",
    "DashboardService"
]
