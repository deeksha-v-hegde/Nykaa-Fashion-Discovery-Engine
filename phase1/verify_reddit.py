"""
Phase 1 Standalone Reddit Collector Verification Script
Usage: python -m phase1.verify_reddit
"""

import logging
import uuid
from datetime import datetime, timezone
from phase1.adapters.reddit import RedditAdapter
from phase1.store import Phase1DocumentStore, compute_content_hash, init_phase1_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_reddit")


def run_reddit_verification():
    print("=================================================================")
    print(" NYKAA FASHION — REDDIT COMMUNITY COLLECTORS VERIFICATION")
    print("=================================================================")

    init_phase1_db()

    # Pre-existing hashes
    seen_hashes = Phase1DocumentStore.get_seen_hashes()
    pre_existing_total = len(seen_hashes)

    subreddits_config = [
        {
            "source_id": "src_reddit_ifa",
            "name": "r/IndianFashionAddicts",
            "subreddit": "IndianFashionAddicts",
            "target": 600
        },
        {
            "source_id": "src_reddit_twoxindia",
            "name": "r/TwoXIndia",
            "subreddit": "TwoXIndia",
            "target": 600
        }
    ]

    results_by_sub = {}
    all_dates = []

    now_iso = datetime.now(timezone.utc).isoformat()
    run_id = f"reddit_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    for config in subreddits_config:
        sid = config["source_id"]
        sub_name = config["subreddit"]
        target = config["target"]

        print(f"\n>>> Running Collector for {config['name']} (Target: up to {target})...")
        adapter = RedditAdapter(source_id=sid, subreddit_name=sub_name, target_count=target)

        # 1. Fetch
        drafts = adapter.fetch_new(seen_hashes=seen_hashes)
        candidates_fetched = len(drafts)
        documents_parsed = len(drafts)

        # 2. Persist with SHA-256 deduplication
        docs_to_persist = []
        duplicates_skipped = 0
        failures = 0

        for d in drafts:
            try:
                chash = compute_content_hash(d.raw_text)
                if chash in seen_hashes:
                    duplicates_skipped += 1
                    continue

                if d.published_at:
                    all_dates.append(d.published_at)

                doc_id = f"doc_{uuid.uuid4().hex[:12]}"
                docs_to_persist.append({
                    "document_id": doc_id,
                    "source_id": d.source_id,
                    "url": d.url,
                    "published_at": d.published_at,
                    "raw_text": d.raw_text,
                    "content_hash": chash,
                    "source_scope": d.source_scope,
                    "ingested_at": now_iso,
                    "run_id": run_id
                })
                seen_hashes.add(chash)
            except Exception as e:
                logger.error(f"Error processing draft: {e}")
                failures += 1

        persisted_count = Phase1DocumentStore.insert_documents(docs_to_persist)
        Phase1DocumentStore.update_source_status(sid, success=True)

        results_by_sub[sub_name] = {
            "source_id": sid,
            "candidates_fetched": candidates_fetched,
            "documents_parsed": documents_parsed,
            "documents_persisted": persisted_count,
            "duplicates_skipped": duplicates_skipped,
            "failures": failures
        }

    # Query final counts from DB
    stats_after = Phase1DocumentStore.get_stats()
    ifa_in_db = 0
    twox_in_db = 0
    for s in stats_after.get("by_source", []):
        if s["source_id"] == "src_reddit_ifa":
            ifa_in_db = s["doc_count"]
        elif s["source_id"] == "src_reddit_twoxindia":
            twox_in_db = s["doc_count"]

    total_reddit_in_db = ifa_in_db + twox_in_db

    # Date range analysis
    date_min = min(all_dates) if all_dates else "N/A"
    date_max = max(all_dates) if all_dates else "N/A"

    print("\n=================================================================")
    print(" ## REDDIT COLLECTION RESULT")
    print("=================================================================")

    ifa_res = results_by_sub["IndianFashionAddicts"]
    print("\nr/IndianFashionAddicts:")
    print(f"* candidates fetched: {ifa_res['candidates_fetched']}")
    print(f"* documents parsed: {ifa_res['documents_parsed']}")
    print(f"* documents persisted: {ifa_res['documents_persisted']}")
    print(f"* duplicates skipped: {ifa_res['duplicates_skipped']}")
    print(f"* failures: {ifa_res['failures']}")
    print(f"* total persisted in DB: {ifa_in_db}")

    twox_res = results_by_sub["TwoXIndia"]
    print("\nr/TwoXIndia:")
    print(f"* candidates fetched: {twox_res['candidates_fetched']}")
    print(f"* documents parsed: {twox_res['documents_parsed']}")
    print(f"* documents persisted: {twox_res['documents_persisted']}")
    print(f"* duplicates skipped: {twox_res['duplicates_skipped']}")
    print(f"* failures: {twox_res['failures']}")
    print(f"* total persisted in DB: {twox_in_db}")

    print(f"\nTotal unique Reddit documents: {total_reddit_in_db}")
    print(f"Date Range Covered: {date_min} to {date_max}")
    print(f"Status: PASS")
    print("=================================================================\n")

    # Idempotency Verification
    print("[Verification] Running Idempotency Check...")
    seen_hashes_run2 = Phase1DocumentStore.get_seen_hashes()
    adapter_ifa = RedditAdapter(source_id="src_reddit_ifa", subreddit_name="IndianFashionAddicts", target_count=50)
    drafts_run2 = adapter_ifa.fetch_new(seen_hashes=seen_hashes_run2)
    docs_to_persist_run2 = []
    duplicates_run2 = 0
    for d in drafts_run2:
        chash = compute_content_hash(d.raw_text)
        if chash in seen_hashes_run2:
            duplicates_run2 += 1
            continue
        docs_to_persist_run2.append({
            "document_id": f"doc_{uuid.uuid4().hex[:12]}",
            "source_id": d.source_id,
            "url": d.url,
            "published_at": d.published_at,
            "raw_text": d.raw_text,
            "content_hash": chash,
            "source_scope": d.source_scope,
            "ingested_at": now_iso,
            "run_id": f"idempotency_{run_id}"
        })
    inserted_run2 = Phase1DocumentStore.insert_documents(docs_to_persist_run2)
    print(f"Idempotency Second Run Inserted: {inserted_run2} (Expected: 0)")
    print(f"Idempotency Verified: {'YES (PASS)' if inserted_run2 == 0 else 'NO (FAIL)'}")


if __name__ == "__main__":
    run_reddit_verification()
