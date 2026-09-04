from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class DocumentDraft(BaseModel):
    """
    Draft document produced by Phase 1 source collectors prior to database persistence.
    Strictly satisfies the Phase 1 Data Contract from architecture.md.
    """
    source_id: str
    url: str
    published_at: Optional[str] = None
    raw_text: str
    source_scope: str = Field(..., pattern="^(nykaa|broader_fashion)$")
    metadata: Optional[Dict[str, Any]] = None


class Collector(ABC):
    """
    Abstract collector interface for all public data source adapters in Phase 1.
    """

    def __init__(self, source_id: str, source_scope: str, platform: str):
        self.source_id = source_id
        self.source_scope = source_scope
        self.platform = platform

    @abstractmethod
    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        """
        Fetch newly available public documents.
        Must respect robots.txt, terms of service, and never attempt bypass of auth/paywalls/CAPTCHAs.
        """
        pass
