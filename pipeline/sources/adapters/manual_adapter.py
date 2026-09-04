import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from pipeline.sources.base import Collector, DocumentDraft

logger = logging.getLogger(__name__)


class ManualUnavailableAdapter(Collector):
    """
    Adapter for sources where automated collection is unavailable or disallowed
    (e.g., YouTube comments requiring authenticated API quotas, Twitter/X paywalled APIs, anti-bot forums).
    Honesty rule: Zero fake documents created, source provenance preserved with 'manual_unavailable' status.
    """

    def __init__(self, source_id: str, source_scope: str, platform: str, reason: str):
        super().__init__(source_id=source_id, source_scope=source_scope, platform=platform)
        self.reason = reason

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        logger.info(f"[{self.source_id}] Source is marked manual_unavailable: {self.reason}. 0 documents fetched.")
        return []
