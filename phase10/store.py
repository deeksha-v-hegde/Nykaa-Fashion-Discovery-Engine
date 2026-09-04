import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("phase10.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase10_schema():
    """Initializes SQLite tables for Phase 10 weekly runs and source registers."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_runs (
            run_id TEXT PRIMARY KEY,
            last_updated TEXT NOT NULL,
            next_scheduled_run TEXT NOT NULL,
            new_documents_this_week INTEGER NOT NULL,
            new_relevant_documents INTEGER NOT NULL,
            sources_successful_count INTEGER NOT NULL,
            sources_failed_count INTEGER NOT NULL,
            sources_total_count INTEGER NOT NULL,
            analysis_status TEXT NOT NULL CHECK(analysis_status IN ('success', 'partial', 'failed')),
            run_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_registers (
            source_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            source_scope TEXT NOT NULL,
            source_type TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('active', 'partial', 'error', 'manual_unavailable')),
            last_fetched_at TEXT,
            error_message TEXT
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weekly_runs_created ON weekly_runs(created_at);")

    conn.commit()
    conn.close()
    logger.info("Phase 10 weekly_runs database schema initialized.")


class Phase10Store:
    """Repository for persisting weekly research runs and source status registers."""

    @staticmethod
    def save_weekly_run(run_data: Dict[str, Any]) -> str:
        init_phase10_schema()
        rid = run_data.get("run_id") or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        now_iso = datetime.now(timezone.utc).isoformat()

        run_data["run_id"] = rid
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO weekly_runs (
                run_id, last_updated, next_scheduled_run, new_documents_this_week,
                new_relevant_documents, sources_successful_count, sources_failed_count,
                sources_total_count, analysis_status, run_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rid,
            run_data.get("last_updated", now_iso),
            run_data.get("next_scheduled_run", now_iso),
            run_data.get("new_documents_this_week", 0),
            run_data.get("new_relevant_documents", 0),
            run_data.get("sources_successful_count", 0),
            run_data.get("sources_failed_count", 0),
            run_data.get("sources_total_count", 0),
            run_data.get("analysis_status", "success"),
            json.dumps(run_data),
            now_iso
        ))

        conn.commit()
        conn.close()
        return rid

    @staticmethod
    def get_latest_weekly_run() -> Optional[Dict[str, Any]]:
        init_phase10_schema()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT run_json FROM weekly_runs ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return json.loads(row["run_json"]) if row else None

    @staticmethod
    def save_source_register(source: Dict[str, Any]):
        init_phase10_schema()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO source_registers (
                source_id, name, platform, source_scope, source_type, status, last_fetched_at, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source["source_id"],
            source["name"],
            source["platform"],
            source["source_scope"],
            source["source_type"],
            source.get("status", "active"),
            source.get("last_fetched_at"),
            source.get("error_message")
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_source_registers() -> List[Dict[str, Any]]:
        init_phase10_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM source_registers ORDER BY source_id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
