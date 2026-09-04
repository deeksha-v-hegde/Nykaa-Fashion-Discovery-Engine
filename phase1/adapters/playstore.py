import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from phase1.base import Collector, DocumentDraft

logger = logging.getLogger(__name__)


class PlayStoreAdapter(Collector):
    """
    Phase 1 Collector adapter for Google Play Store public reviews of Nykaa Fashion.
    Scope: nykaa
    Mode: automated
    """

    def __init__(self, source_id: str = "src_playstore_nykaa", source_scope: str = "nykaa"):
        super().__init__(source_id=source_id, source_scope=source_scope, platform="Google Play Store")

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        logger.info(f"[{self.source_id}] Ingesting Google Play Store reviews for Nykaa Fashion...")
        drafts: List[DocumentDraft] = []
        
        # Check for 2000 scraped reviews first, then fallback to seed_corpus.json
        playstore_path = Path("data/playstore_2000_reviews.json")
        seed_path = Path("data/seed_corpus.json")

        if playstore_path.exists():
            with open(playstore_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    drafts.append(DocumentDraft(
                        source_id=self.source_id,
                        url=item["url"],
                        published_at=item.get("published_at"),
                        raw_text=item["raw_text"],
                        source_scope=self.source_scope,
                        metadata={
                            "platform": self.platform,
                            "app_id": "com.fsn.nykaa",
                            "rating": item.get("rating"),
                            "thumbs_up": item.get("thumbs_up", 0),
                            "user_name": item.get("user_name")
                        }
                    ))
        elif seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                all_items = json.load(f)
                playstore_items = [i for i in all_items if i.get("source_id") == self.source_id]
                for item in playstore_items:
                    drafts.append(DocumentDraft(
                        source_id=self.source_id,
                        url=item["url"],
                        published_at=item.get("published_at"),
                        raw_text=item["raw_text"],
                        source_scope=self.source_scope,
                        metadata={"platform": self.platform, "app_id": "com.fsn.nykaa"}
                    ))

        logger.info(f"[{self.source_id}] Successfully loaded {len(drafts)} drafts.")
        return drafts
