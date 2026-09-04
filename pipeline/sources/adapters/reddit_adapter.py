import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pipeline.sources.base import Collector, DocumentDraft

logger = logging.getLogger(__name__)


class RedditAdapter(Collector):
    """
    Collector adapter for Reddit fashion communities (r/IndianFashionAddicts, r/TwoXIndia).
    Tagged strictly with source_scope = 'broader_fashion'.
    """

    def __init__(self, source_id: str, subreddit_name: str):
        super().__init__(source_id=source_id, source_scope="broader_fashion", platform="Reddit")
        self.subreddit_name = subreddit_name

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        logger.info(f"[{self.source_id}] Ingesting public discussions from r/{self.subreddit_name}...")
        drafts: List[DocumentDraft] = []
        seed_path = Path("data/seed_corpus.json")

        if seed_path.exists():
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    all_items = json.load(f)
                    reddit_items = [i for i in all_items if i.get("source_id") == self.source_id]
                    for item in reddit_items:
                        drafts.append(DocumentDraft(
                            source_id=self.source_id,
                            url=item["url"],
                            published_at=item.get("published_at"),
                            raw_text=item["raw_text"],
                            source_scope=self.source_scope,
                            metadata={"platform": self.platform, "subreddit": self.subreddit_name}
                        ))
            except Exception as e:
                logger.error(f"[{self.source_id}] Error reading Reddit corpus: {e}")
                raise

        logger.info(f"[{self.source_id}] Ingested {len(drafts)} drafts from r/{self.subreddit_name}.")
        return drafts
