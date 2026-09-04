import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

from phase1.base import Collector
from phase1.store import Phase1DocumentStore, compute_content_hash, get_db_connection, init_phase1_db
from phase1.adapters.playstore import PlayStoreAdapter
from phase1.adapters.appstore import AppStoreAdapter
from phase1.adapters.reddit import RedditAdapter
from phase1.adapters.manual import ManualUnavailableAdapter

logger = logging.getLogger("phase1.ingest")


class Phase1IngestionJob:
    """
    Phase 1 Ingestion Workflow Runner.
    Brings legally accessible public documents into corpus store with hashes and provenance.
    """

    def __init__(self, sources_yaml_path: str = "config/sources.yaml"):
        self.sources_yaml_path = Path(sources_yaml_path)
        init_phase1_db()

    def load_sources(self) -> List[Dict[str, Any]]:
        if not self.sources_yaml_path.exists():
            raise FileNotFoundError(f"Source configuration file not found at {self.sources_yaml_path}")
        with open(self.sources_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("sources", [])

    def resolve_collector(self, source_conf: Dict[str, Any]) -> Collector:
        sid = source_conf["source_id"]
        scope = source_conf["source_scope"]
        platform = source_conf["platform"]
        mode = source_conf["collection_mode"]

        if mode == "manual_unavailable":
            return ManualUnavailableAdapter(
                source_id=sid,
                source_scope=scope,
                platform=platform,
                reason="Manual collection / authentication / bot protection"
            )

        if sid == "src_playstore_nykaa":
            return PlayStoreAdapter(source_id=sid, source_scope=scope)
        elif sid == "src_appstore_nykaa":
            return AppStoreAdapter(source_id=sid, source_scope=scope)
        elif sid == "src_reddit_ifa":
            return RedditAdapter(source_id=sid, subreddit_name="IndianFashionAddicts")
        elif sid == "src_reddit_twoxindia":
            return RedditAdapter(source_id=sid, subreddit_name="TwoXIndia")
        else:
            return ManualUnavailableAdapter(
                source_id=sid,
                source_scope=scope,
                platform=platform,
                reason="No automated adapter configured"
            )

    def run(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        run_id = run_id or f"p1_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now(timezone.utc).isoformat()
        logger.info(f"=== [Phase 1 Ingestion] Starting run: {run_id} ===")

        # 1. Sync registered sources into database
        sources_list = self.load_sources()
        Phase1DocumentStore.sync_sources(sources_list)

        # 2. Get seen hashes to prevent duplicate insertions
        seen_hashes = Phase1DocumentStore.get_seen_hashes()
        logger.info(f"[Phase 1] Pre-existing corpus hashes: {len(seen_hashes)}")

        total_attempted = 0
        total_inserted = 0
        total_skipped_duplicate = 0
        failed_sources = 0
        per_source_stats: List[Dict[str, Any]] = []

        # 3. Ingest each source with per-source exception isolation
        for source_conf in sources_list:
            sid = source_conf["source_id"]
            collector = self.resolve_collector(source_conf)

            stat = {
                "source_id": sid,
                "name": source_conf["name"],
                "platform": source_conf["platform"],
                "scope": source_conf["source_scope"],
                "mode": source_conf["collection_mode"],
                "attempted": 0,
                "inserted": 0,
                "skipped_duplicate": 0,
                "status": "success",
                "error": None
            }

            try:
                drafts = collector.fetch_new(seen_hashes=seen_hashes)
                stat["attempted"] = len(drafts)
                total_attempted += len(drafts)

                docs_to_persist = []
                for draft in drafts:
                    chash = compute_content_hash(draft.raw_text)
                    if chash in seen_hashes:
                        stat["skipped_duplicate"] += 1
                        total_skipped_duplicate += 1
                        continue

                    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
                    now_iso = datetime.now(timezone.utc).isoformat()

                    docs_to_persist.append({
                        "document_id": doc_id,
                        "source_id": draft.source_id,
                        "url": draft.url,
                        "published_at": draft.published_at,
                        "raw_text": draft.raw_text,
                        "content_hash": chash,
                        "source_scope": draft.source_scope,
                        "ingested_at": now_iso,
                        "run_id": run_id
                    })
                    seen_hashes.add(chash)

                inserted_count = Phase1DocumentStore.insert_documents(docs_to_persist)
                stat["inserted"] = inserted_count
                total_inserted += inserted_count

                Phase1DocumentStore.update_source_status(sid, success=True)

            except Exception as e:
                logger.error(f"[Phase 1] Error ingesting source {sid}: {e}", exc_info=True)
                failed_sources += 1
                stat["status"] = "failed"
                stat["error"] = str(e)
                Phase1DocumentStore.update_source_status(sid, success=False, error_message=str(e))

            per_source_stats.append(stat)

        completed_at = datetime.now(timezone.utc).isoformat()
        overall_status = "success" if failed_sources == 0 else ("partial" if total_inserted > 0 else "failed")

        # 4. Write Ingest Log
        conn = get_db_connection()
        cursor = conn.cursor()
        log_id = f"log_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO ingest_logs (
                log_id, run_id, started_at, completed_at, attempted,
                inserted, skipped_duplicate, failed_sources, status, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            run_id,
            started_at,
            completed_at,
            total_attempted,
            total_inserted,
            total_skipped_duplicate,
            failed_sources,
            overall_status,
            json.dumps(per_source_stats)
        ))
        conn.commit()
        conn.close()

        summary = {
            "phase": "Phase 1 - Ingestion",
            "run_id": run_id,
            "status": overall_status,
            "started_at": started_at,
            "completed_at": completed_at,
            "attempted": total_attempted,
            "inserted": total_inserted,
            "skipped_duplicate": total_skipped_duplicate,
            "failed_sources": failed_sources,
            "per_source_stats": per_source_stats
        }
        logger.info(f"=== [Phase 1 Ingestion] Finished: {total_inserted} inserted, {total_skipped_duplicate} skipped duplicate, status: {overall_status} ===")
        return summary
