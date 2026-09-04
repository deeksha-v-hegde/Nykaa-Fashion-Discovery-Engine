import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from google_play_scraper import Sort, reviews

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("playstore_scraper")


def scrape_nykaa_playstore_reviews(
    app_id: str = "com.fsn.nykaa",
    target_count: int = 2000,
    output_file: str = "data/playstore_2000_reviews.json"
) -> List[Dict[str, Any]]:
    """
    Scrapes public user reviews for Nykaa from Google Play Store using the public endpoint.
    Retrieves up to `target_count` reviews sorted by newest/most relevant.
    """
    logger.info(f"Starting Play Store scraping for package: {app_id} (Target: {target_count} reviews)...")
    
    all_reviews = []
    continuation_token = None
    batch_size = 200  # Google play scraper maximum per batch
    
    # Sort strategies to ensure diversity: NEWEST and MOST_RELEVANT
    sort_modes = [Sort.NEWEST, Sort.MOST_RELEVANT]

    for sort_mode in sort_modes:
        if len(all_reviews) >= target_count:
            break
            
        mode_name = "NEWEST" if sort_mode == Sort.NEWEST else "MOST_RELEVANT"
        logger.info(f"Fetching reviews with sort mode: {mode_name}...")
        
        continuation_token = None
        while len(all_reviews) < target_count:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang="en",
                    country="in",
                    sort=sort_mode,
                    count=batch_size,
                    continuation_token=continuation_token
                )
                
                if not result:
                    logger.info("No more reviews returned in this batch.")
                    break

                for r in result:
                    content = (r.get("content") or "").strip()
                    # Keep reviews with meaningful text length
                    if len(content) >= 10:
                        review_id = str(r.get("reviewId") or f"gp_{hash(content)}")
                        dt = r.get("at")
                        published_iso = dt.isoformat() if isinstance(dt, datetime) else str(dt)

                        all_reviews.append({
                            "source_id": "src_playstore_nykaa",
                            "platform": "Google Play Store",
                            "source_scope": "nykaa",
                            "review_id": review_id,
                            "url": f"https://play.google.com/store/apps/details?id={app_id}&reviewId={review_id}",
                            "published_at": published_iso,
                            "rating": r.get("score"),
                            "thumbs_up": r.get("thumbsUpCount", 0),
                            "raw_text": content,
                            "user_name": r.get("userName", "Anonymous User"),
                            "app_version": r.get("reviewCreatedVersion")
                        })
                
                logger.info(f"Collected {len(all_reviews)} / {target_count} reviews...")
                
                if not continuation_token or len(all_reviews) >= target_count:
                    break

                time.sleep(0.5)  # Politeness delay

            except Exception as e:
                logger.error(f"Error during batch scrape: {e}")
                time.sleep(2)
                break

    # Deduplicate by review_id / raw_text
    seen_texts = set()
    unique_reviews = []
    for rev in all_reviews:
        txt_norm = " ".join(rev["raw_text"].lower().split())
        if txt_norm not in seen_texts:
            seen_texts.add(txt_norm)
            unique_reviews.append(rev)

    final_reviews = unique_reviews[:target_count]
    logger.info(f"Total unique reviews collected: {len(final_reviews)}")

    # Save to JSON file
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_reviews, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(final_reviews)} reviews to {out_path.resolve()}")
    return final_reviews


if __name__ == "__main__":
    scrape_nykaa_playstore_reviews(target_count=2000)
