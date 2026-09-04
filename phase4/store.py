import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("phase4.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase4_schema():
    """Initializes schema for Phase 4 query traces."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_traces (
            trace_id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            filters TEXT,
            retrieved_chunk_ids TEXT,
            top_score REAL,
            status TEXT NOT NULL,
            grounded_answer TEXT,
            nykaa_evidence_limited INTEGER NOT NULL DEFAULT 0,
            latency_ms REAL,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_created ON query_traces(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_status ON query_traces(status);")

    conn.commit()
    conn.close()
    logger.info("Phase 4 query traces schema initialized.")


class Phase4Store:
    """Repository for storing and retrieving Phase 4 query traces."""

    @staticmethod
    def save_trace(
        query: str,
        filters: Dict[str, Any],
        retrieved_chunk_ids: List[str],
        top_score: float,
        status: str,
        grounded_answer: str,
        nykaa_evidence_limited: bool,
        latency_ms: float,
        trace_id: Optional[str] = None
    ) -> str:
        init_phase4_schema()
        tid = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO query_traces (
                trace_id, query, filters, retrieved_chunk_ids,
                top_score, status, grounded_answer, nykaa_evidence_limited,
                latency_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tid,
            query,
            json.dumps(filters or {}),
            json.dumps(retrieved_chunk_ids or []),
            top_score,
            status,
            grounded_answer,
            1 if nykaa_evidence_limited else 0,
            latency_ms,
            now_iso
        ))
        conn.commit()
        conn.close()
        return tid

    @staticmethod
    def get_traces(limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM query_traces ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        for r in rows:
            r["filters"] = json.loads(r["filters"] or "{}")
            r["retrieved_chunk_ids"] = json.loads(r["retrieved_chunk_ids"] or "[]")
            r["nykaa_evidence_limited"] = bool(r["nykaa_evidence_limited"])
        return rows
