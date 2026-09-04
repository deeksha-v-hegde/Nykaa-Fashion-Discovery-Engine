import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import httpx

from phase1.base import Collector, DocumentDraft

logger = logging.getLogger("phase1.adapters.reddit")


class RedditAdapter(Collector):
    """
    Phase 1 Collector adapter for Reddit fashion communities.
    Supports r/IndianFashionAddicts and r/TwoXIndia.
    Fetches real public community discussions with timestamp-based pagination,
    fashion & wishlist domain relevance filtering, provenance preservation,
    and SHA-256 deduplication.

    Scope: broader_fashion
    Source Type: community_discussion
    Mode: automated
    """

    # Keyword filters for general subreddits (e.g. TwoXIndia) to retain relevant fashion/shopping discussions
    FASHION_SHOPPING_KEYWORDS = [
        "fashion", "clothes", "clothing", "dress", "kurta", "kurti", "saree", "ethnic", "western",
        "nykaa", "myntra", "ajio", "zara", "h&m", "urbanic", "westside", "meesho", "snitch", "savana", "newme",
        "size", "sizing", "fit", "fitting", "fabric", "quality", "material", "brand", "brands",
        "wishlist", "wishlisting", "cart", "buy", "shopping", "purchase", "recommendation", "outfit",
        "styling", "return", "exchange", "refund", "heels", "shoes", "footwear", "lingerie", "bra",
        "jeans", "skirt", "top", "blouse", "dupatta", "lehenga", "jewellery", "jewelry", "haul"
    ]

    def __init__(self, source_id: str, subreddit_name: str, target_count: int = 600):
        super().__init__(source_id=source_id, source_scope="broader_fashion", platform="Reddit")
        self.subreddit_name = subreddit_name
        self.target_count = target_count

    def fetch_new(
        self,
        since: Optional[datetime] = None,
        seen_hashes: Optional[Set[str]] = None
    ) -> List[DocumentDraft]:
        """
        Fetches real public posts from the subreddit using paginated public archives.
        Extracts title, selftext, author, ISO timestamp, score, and permalink.
        """
        logger.info(f"[{self.source_id}] Starting collection for r/{self.subreddit_name} (Target: up to {self.target_count})...")

        drafts: List[DocumentDraft] = []
        unique_posts: Dict[str, Dict[str, Any]] = {}
        last_before: Optional[int] = None
        max_pages = 35
        pages_fetched = 0

        # Public Reddit archive endpoint with timestamp pagination
        base_url = "https://arctic-shift.photon-reddit.com/api/posts/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NykaaFashionResearch/1.0",
            "Accept": "application/json"
        }

        with httpx.Client(timeout=15.0, headers=headers) as client:
            while len(unique_posts) < self.target_count and pages_fetched < max_pages:
                pages_fetched += 1
                params: Dict[str, Any] = {
                    "subreddit": self.subreddit_name,
                    "limit": 100
                }
                if last_before:
                    params["before"] = last_before

                try:
                    resp = client.get(base_url, params=params)
                    if resp.status_code == 200:
                        posts = resp.json().get("data", [])
                        if not posts:
                            logger.info(f"[{self.source_id}] No more posts returned at page {pages_fetched}.")
                            break

                        for p in posts:
                            created_utc = p.get("created_utc")
                            if created_utc:
                                last_before = created_utc

                            pid = str(p.get("id") or "")
                            title = (p.get("title") or "").strip()
                            selftext = (p.get("selftext") or "").strip()

                            # Filter out empty or deleted posts
                            if not title or title.startswith("[deleted]") or title.startswith("[removed]"):
                                continue
                            if selftext in ["[removed]", "[deleted]"]:
                                selftext = ""

                            full_text = f"{title}\n\n{selftext}".strip() if selftext else title

                            # Apply domain keyword relevance filter for broader general communities
                            if self.subreddit_name.lower() == "twoxindia":
                                lower_text = full_text.lower()
                                if not any(kw in lower_text for kw in self.FASHION_SHOPPING_KEYWORDS):
                                    continue

                            # Filter out very short low-information snippets
                            if pid and len(full_text) >= 20 and pid not in unique_posts:
                                # Format ISO timestamp
                                pub_iso = None
                                if created_utc:
                                    try:
                                        pub_iso = datetime.fromtimestamp(created_utc, timezone.utc).isoformat()
                                    except Exception:
                                        pass

                                permalink = p.get("permalink") or f"/r/{self.subreddit_name}/comments/{pid}/"
                                full_url = f"https://www.reddit.com{permalink}" if not permalink.startswith("http") else permalink

                                unique_posts[pid] = {
                                    "external_id": pid,
                                    "title": title,
                                    "selftext": selftext,
                                    "raw_text": full_text,
                                    "author": p.get("author") or "Anonymous User",
                                    "url": full_url,
                                    "published_at": pub_iso,
                                    "created_utc": created_utc,
                                    "score": p.get("score", 1),
                                    "subreddit": self.subreddit_name
                                }

                                if len(unique_posts) >= self.target_count:
                                    break

                    elif resp.status_code == 429:
                        logger.warning(f"[{self.source_id}] Rate limited, backing off...")
                        time.sleep(2.0)
                    else:
                        logger.warning(f"[{self.source_id}] HTTP {resp.status_code} on page {pages_fetched}")

                    time.sleep(0.15)  # Sensible polite rate throttling

                except Exception as e:
                    logger.warning(f"[{self.source_id}] Error fetching page {pages_fetched}: {e}")
                    time.sleep(0.5)

        logger.info(f"[{self.source_id}] Retrieved {len(unique_posts)} posts from r/{self.subreddit_name} across {pages_fetched} pages.")

        # Also preserve existing seed entries if present
        seed_path = Path("data/seed_corpus.json")
        if seed_path.exists():
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed_data = json.load(f)
                    for item in seed_data:
                        if item.get("source_id") == self.source_id:
                            sid = item["url"]
                            if sid not in unique_posts:
                                unique_posts[sid] = {
                                    "external_id": sid,
                                    "title": item["raw_text"][:60],
                                    "selftext": item["raw_text"],
                                    "raw_text": item["raw_text"],
                                    "author": "Community Member",
                                    "url": item["url"],
                                    "published_at": item.get("published_at"),
                                    "subreddit": self.subreddit_name
                                }
            except Exception as e:
                logger.warning(f"Failed to read seed corpus for {self.source_id}: {e}")

        # Save snapshot to disk
        out_dir = Path("data")
        out_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = out_dir / f"reddit_{self.subreddit_name.lower()}_posts.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(list(unique_posts.values()), f, indent=2, ensure_ascii=False)

        # Convert to DocumentDraft instances
        for pid, post in unique_posts.items():
            drafts.append(DocumentDraft(
                source_id=self.source_id,
                url=post["url"],
                published_at=post.get("published_at"),
                raw_text=post["raw_text"],
                source_scope=self.source_scope,
                metadata={
                    "platform": self.platform,
                    "subreddit": self.subreddit_name,
                    "external_id": post.get("external_id"),
                    "author": post.get("author"),
                    "title": post.get("title"),
                    "score": post.get("score"),
                    "source_type": "community_discussion"
                }
            ))

        logger.info(f"[{self.source_id}] Successfully generated {len(drafts)} DocumentDraft records.")
        return drafts
