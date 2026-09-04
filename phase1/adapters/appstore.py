import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import httpx

from phase1.base import Collector, DocumentDraft

logger = logging.getLogger("phase1.adapters.appstore")


class AppStoreAdapter(Collector):
    """
    Phase 1 Collector adapter for Apple App Store public reviews of Nykaa Fashion.
    Fetches real public user reviews via Apple's official iTunes customer reviews RSS endpoint.
    Handles pagination, multiple sort strategies, multi-country storefronts, request throttling,
    and fallback to local seed data.
    
    Scope: nykaa
    Mode: automated
    """

    # Official Nykaa Fashion App Store ID
    APP_ID = "1439872423"
    APP_NAME = "nykaa-fashion-shopping-app"

    def __init__(self, source_id: str = "src_appstore_nykaa", source_scope: str = "nykaa"):
        super().__init__(source_id=source_id, source_scope=source_scope, platform="Apple App Store")

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        """
        Fetches public customer reviews from Apple App Store RSS API.
        Respects rate limits, public accessibility, and never fabricates reviews.
        """
        logger.info(f"[{self.source_id}] Starting Apple App Store public review collection for App ID {self.APP_ID}...")
        
        drafts: List[DocumentDraft] = []
        unique_collected: Dict[str, Dict[str, Any]] = {}
        
        # 1. Fetch live reviews from Apple's public iTunes Customer Reviews API
        countries = ["in", "us", "gb", "ae", "ca", "sg", "au"]
        sort_modes = ["mostRecent", "mostHelpful"]
        
        headers = {
            "User-Agent": "iTunes/12.11.3 (Windows; Microsoft Windows 10 x64)",
            "Accept": "application/json"
        }

        with httpx.Client(timeout=10.0, headers=headers) as client:
            for country in countries:
                for sort_by in sort_modes:
                    for page in range(1, 11):
                        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={self.APP_ID}/sortBy={sort_by}/json"
                        try:
                            resp = client.get(url)
                            if resp.status_code == 200:
                                data = resp.json()
                                entries = data.get("feed", {}).get("entry", [])
                                if isinstance(entries, dict):
                                    entries = [entries]

                                for entry in entries:
                                    if "content" in entry and isinstance(entry["content"], dict):
                                        rev_id = str(entry.get("id", {}).get("label") or "")
                                        content = (entry.get("content", {}).get("label") or "").strip()
                                        title = (entry.get("title", {}).get("label") or "").strip()
                                        author = entry.get("author", {}).get("name", {}).get("label", "Anonymous User")
                                        rating_str = entry.get("im:rating", {}).get("label")
                                        updated_str = entry.get("updated", {}).get("label")

                                        # Format combined text if title adds context
                                        raw_text = f"{title} - {content}" if title and title != content and not content.startswith(title) else content
                                        
                                        if rev_id and len(content) >= 10 and rev_id not in unique_collected:
                                            unique_collected[rev_id] = {
                                                "review_id": rev_id,
                                                "url": f"https://apps.apple.com/{country}/app/{self.APP_NAME}/id{self.APP_ID}?reviewId={rev_id}",
                                                "published_at": updated_str,
                                                "author": author,
                                                "rating": int(rating_str) if rating_str and rating_str.isdigit() else None,
                                                "raw_text": raw_text,
                                                "country": country
                                            }

                            time.sleep(0.1)  # Throttling between pages

                        except Exception as e:
                            logger.warning(f"Error fetching page {page} for {country}/{sort_by}: {e}")
                            time.sleep(0.2)

        logger.info(f"[{self.source_id}] Collected {len(unique_collected)} live reviews from Apple App Store RSS.")

        # 2. Also incorporate local seed entries if any
        seed_path = Path("data/seed_corpus.json")
        if seed_path.exists():
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed_data = json.load(f)
                    for item in seed_data:
                        if item.get("source_id") == self.source_id:
                            sid = item["url"]
                            if sid not in unique_collected:
                                unique_collected[sid] = {
                                    "review_id": sid,
                                    "url": item["url"],
                                    "published_at": item.get("published_at"),
                                    "author": "Verified Customer",
                                    "rating": None,
                                    "raw_text": item["raw_text"],
                                    "country": "in"
                                }
            except Exception as e:
                logger.warning(f"Failed to read seed corpus: {e}")

        # 3. Save snapshot to data/appstore_reviews.json
        output_file = Path("data/appstore_reviews.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(list(unique_collected.values()), f, indent=2, ensure_ascii=False)

        # 4. Construct DocumentDraft objects
        for rev_id, r in unique_collected.items():
            drafts.append(DocumentDraft(
                source_id=self.source_id,
                url=r["url"],
                published_at=r.get("published_at"),
                raw_text=r["raw_text"],
                source_scope=self.source_scope,
                metadata={
                    "platform": self.platform,
                    "app_id": self.APP_ID,
                    "external_id": r.get("review_id"),
                    "author": r.get("author"),
                    "rating": r.get("rating"),
                    "country": r.get("country")
                }
            ))

        logger.info(f"[{self.source_id}] Successfully generated {len(drafts)} DocumentDraft records.")
        return drafts
