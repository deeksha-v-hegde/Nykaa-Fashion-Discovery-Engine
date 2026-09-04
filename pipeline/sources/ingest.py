import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

from db.store import DocumentStore, compute_content_hash, get_db_connection, init_db
from pipeline.sources.base import Collector, DocumentDraft
from pipeline.sources.adapters.playstore_adapter import PlayStoreAdapter
from pipeline.sources.adapters.appstore_adapter import AppStoreAdapter
from pipeline.sources.adapters.reddit_adapter import RedditAdapter
from pipeline.sources.adapters.manual_adapter import ManualUnavailableAdapter

logger = logging.getLogger(__name__)


class IngestJob:
    """
    Executes Phase 1 data ingestion workflow.
    - Synchronizes source registry.
    - Runs collectors for automated sources.
    - Computes SHA-256 content hashes.
    - Skips duplicate documents.
    - Persists document rows and per-source status.
    - Logs overall ingest run summary.
    """

    def __init__(self, sources_config_path: str = "config/sources.yaml"):
        self.sources_config_path = Path(sources_config_path)
        init_db()

    def load_sources_registry(self) -> List[Dict[str, Any]]:
        if not self.sources_config_path.exists():
            raise FileNotFoundError(f"Source configuration file not found at {self.sources_config_path}")
        with open(self.sources_config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("sources", [])

    def get_collector_for_source(self, source_conf: Dict[str, Any]) -> Collector:
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
                reason="No automated adapter registered"
            )

    def run(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        run_id = run_id or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now(timezone.utc).isoformat()
        logger.info(f"=== Starting Ingestion Job [{run_id}] ===")

        # 1. Sync sources from registry
        sources_list = self.load_sources_registry()
        DocumentStore.sync_sources_from_registry(sources_list)

        # 2. Retrieve existing content hashes for deduplication
        seen_hashes = DocumentStore.get_seen_hashes()
        logger.info(f"Corpus currently has {len(seen_hashes)} indexed hashes.")

        total_attempted = 0
        total_inserted = 0
        total_skipped_duplicate = 0
        failed_sources = 0
        per_source_results: List[Dict[str, Any]] = []

        # 3. Process each source independently (failure isolation)
        for source_conf in sources_list:
            sid = source_conf["source_id"]
            collector = self.get_collector_for_source(source_conf)

            source_stat = {
                "source_id": sid,
                "name": source_conf["name"],
                "platform": source_conf["platform"],
                "collection_mode": source_conf["collection_mode"],
                "scope": source_conf["source_scope"],
                "attempted": 0,
                "inserted": 0,
                "skipped_duplicate": 0,
                "status": "success",
                "error": None
            }

            try:
                drafts = collector.fetch_new(seen_hashes=seen_hashes)
                source_stat["attempted"] = len(drafts)
                total_attempted += len(drafts)

                docs_to_insert = []
                for draft in drafts:
                    chash = compute_content_hash(draft.raw_text)
                    if chash in seen_hashes:
                        source_stat["skipped_duplicate"] += 1
                        total_skipped_duplicate += 1
                        continue

                    # New unique document
                    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
                    now_iso = datetime.now(timezone.utc).isoformat()

                    docs_to_insert.append({
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

                inserted_count = DocumentStore.insert_documents(docs_to_insert)
                source_stat["inserted"] = inserted_count
                total_inserted += inserted_count

                # Update source last_success in DB
                DocumentStore.update_source_status(sid, success=True)

            except Exception as e:
                logger.error(f"Failed to ingest source [{sid}]: {e}", exc_info=True)
                failed_sources += 1
                source_stat["status"] = "failed"
                source_stat["error"] = str(e)
                DocumentStore.update_source_status(sid, success=False, error_message=str(e))

            per_source_results.append(source_stat)

        completed_at = datetime.now(timezone.utc).isoformat()
        overall_status = "success" if failed_sources == 0 else ("partial" if total_inserted > 0 else "failed")

        # 4. Record Ingest Run Log
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
            json.dumps(per_source_results)
        ))
        conn.commit()
        conn.close()

        summary = {
            "run_id": run_id,
            "status": overall_status,
            "started_at": started_at,
            "completed_at": completed_at,
            "attempted": total_attempted,
            "inserted": total_inserted,
            "skipped_duplicate": total_skipped_duplicate,
            "failed_sources": failed_sources,
            "per_source_results": per_source_results
        }
        logger.info(f"=== Ingestion Complete: {total_inserted} new docs inserted, {total_skipped_duplicate} skipped duplicate, status: {overall_status} ===")
        return summary
