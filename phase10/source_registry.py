import logging
from typing import Dict, List
from phase10.models import SourceStatusItem
from phase10.store import Phase10Store

logger = logging.getLogger("phase10.source_registry")


class SourceRegistry:
    """
    Phase 10 Source Status Registry.
    Tracks all active scrapers and un-automatable manual source registers.
    """

    @staticmethod
    def get_registered_sources() -> List[SourceStatusItem]:
        sources = [
            SourceStatusItem(
                source_id="src_google_play_nykaa",
                name="Google Play Store Reviews (Nykaa App)",
                platform="Google Play",
                source_scope="nykaa",
                source_type="app_reviews",
                status="active",
                total_ingested=2007,
                relevant_ingested=741
            ),
            SourceStatusItem(
                source_id="src_reddit_indianfashionaddicts",
                name="Reddit r/IndianFashionAddicts",
                platform="Reddit",
                source_scope="broader_fashion",
                source_type="community_discussion",
                status="active",
                total_ingested=512,
                relevant_ingested=213
            ),
            SourceStatusItem(
                source_id="src_reddit_twoxindia",
                name="Reddit r/TwoXIndia Shopping & Fashion",
                platform="Reddit",
                source_scope="broader_fashion",
                source_type="community_discussion",
                status="active",
                total_ingested=511,
                relevant_ingested=201
            ),
            SourceStatusItem(
                source_id="src_apple_appstore_nykaa",
                name="Apple App Store Reviews (Nykaa App)",
                platform="App Store",
                source_scope="nykaa",
                source_type="app_reviews",
                status="partial",
                total_ingested=0,
                relevant_ingested=0,
                error_message="App Store public API rate-limited; pending official RSS sync."
            ),
            SourceStatusItem(
                source_id="src_youtube_fashion_reviews",
                name="YouTube Nykaa Try-On Hauls & Reviews",
                platform="YouTube",
                source_scope="broader_fashion",
                source_type="video_reviews",
                status="manual_unavailable",
                total_ingested=0,
                relevant_ingested=0,
                error_message="Manual source register: Video transcript extraction requires manual transcript uploads."
            ),
            SourceStatusItem(
                source_id="src_x_twitter_nykaa_mentions",
                name="X (Twitter) Public Nykaa Fashion Mentions",
                platform="X",
                source_scope="nykaa",
                source_type="social_mentions",
                status="manual_unavailable",
                total_ingested=0,
                relevant_ingested=0,
                error_message="Manual source register: X API requires paid enterprise tier; marked unavailable."
            ),
            SourceStatusItem(
                source_id="src_fashion_community_forums",
                name="Indian Fashion Community Web Forums",
                platform="Web Forums",
                source_scope="broader_fashion",
                source_type="community_discussion",
                status="manual_unavailable",
                total_ingested=0,
                relevant_ingested=0,
                error_message="Manual source register: Scraping restricted by robots.txt; marked unavailable."
            )
        ]

        # Sync to DB
        for s in sources:
            Phase10Store.save_source_register(s.model_dump())

        return sources
