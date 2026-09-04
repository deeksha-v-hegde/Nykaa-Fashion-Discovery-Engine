import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("phase6.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase6_schema():
    """Initializes schema for Phase 6 quantification snapshots and gaps catalogue."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quantification_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            sample_size_n INTEGER NOT NULL,
            report_json TEXT NOT NULL,
            computed_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coverage_gaps (
            gap_id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            impact TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_computed ON quantification_snapshots(computed_at);")

    conn.commit()
    conn.close()
    logger.info("Phase 6 quantification and coverage_gaps schema initialized.")


class Phase6Store:
    """Repository for persisting Phase 6 quantification reports and coverage gap records."""

    @staticmethod
    def save_snapshot(sample_size_n: int, report_dict: Dict[str, Any]) -> str:
        init_phase6_schema()
        sid = f"snap_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quantification_snapshots (
                snapshot_id, sample_size_n, report_json, computed_at
            ) VALUES (?, ?, ?, ?)
        """, (sid, sample_size_n, json.dumps(report_dict), now_iso))
        conn.commit()
        conn.close()
        return sid

    @staticmethod
    def get_latest_snapshot() -> Optional[Dict[str, Any]]:
        init_phase6_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quantification_snapshots ORDER BY computed_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            res = dict(row)
            res["report"] = json.loads(res["report_json"])
            return res
        return None

    @staticmethod
    def save_gaps(gaps: List[Dict[str, Any]]) -> int:
        if not gaps:
            return 0
        init_phase6_schema()
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        cursor = conn.cursor()

        payload = [
            (
                g["gap_id"],
                g["category"],
                g["title"],
                g["description"],
                g["impact"],
                g["recommended_action"],
                now_iso
            )
            for g in gaps
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO coverage_gaps (
                gap_id, category, title, description, impact, recommended_action, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, payload)

        conn.commit()
        conn.close()
        return len(gaps)

    @staticmethod
    def get_all_gaps() -> List[Dict[str, Any]]:
        init_phase6_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coverage_gaps ORDER BY category ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
