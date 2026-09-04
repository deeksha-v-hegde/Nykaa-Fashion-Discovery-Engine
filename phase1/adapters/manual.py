import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from phase1.base import Collector, DocumentDraft

logger = logging.getLogger(__name__)


class ManualUnavailableAdapter(Collector):
    """
    Phase 1 Adapter for non-automatable or restricted sources
    (e.g., YouTube video comments, X/Twitter paywalled API, protected forums).
    Architecture Rule: Mark honestly as manual_unavailable with zero fake rows.
    """

    def __init__(self, source_id: str, source_scope: str, platform: str, reason: str):
        super().__init__(source_id=source_id, source_scope=source_scope, platform=platform)
        self.reason = reason

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        logger.info(f"[{self.source_id}] Source is manual_unavailable ({self.reason}). Returning 0 documents.")
        return []
