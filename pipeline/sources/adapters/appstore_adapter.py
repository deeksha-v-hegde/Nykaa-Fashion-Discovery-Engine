import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pipeline.sources.base import Collector, DocumentDraft

logger = logging.getLogger(__name__)


class AppStoreAdapter(Collector):
    """
    Collector adapter for Apple App Store public reviews.
    """

    def __init__(self, source_id: str = "src_appstore_nykaa", source_scope: str = "nykaa"):
        super().__init__(source_id=source_id, source_scope=source_scope, platform="Apple App Store")

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        logger.info(f"[{self.source_id}] Starting App Store review ingestion...")
        drafts: List[DocumentDraft] = []
        seed_path = Path("data/seed_corpus.json")

        if seed_path.exists():
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    all_items = json.load(f)
                    appstore_items = [i for i in all_items if i.get("source_id") == self.source_id]
                    for item in appstore_items:
                        drafts.append(DocumentDraft(
                            source_id=self.source_id,
                            url=item["url"],
                            published_at=item.get("published_at"),
                            raw_text=item["raw_text"],
                            source_scope=self.source_scope,
                            metadata={"platform": self.platform, "app_id": "1453295843"}
                        ))
            except Exception as e:
                logger.error(f"[{self.source_id}] Error reading seed dataset: {e}")
                raise

        logger.info(f"[{self.source_id}] Ingested {len(drafts)} drafts from App Store.")
        return drafts
