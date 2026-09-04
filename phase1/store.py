import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite database connection with row factory enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase1_db():
    """Initializes the database schema for Phase 1 Ingestion."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            source_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_scope TEXT NOT NULL CHECK(source_scope IN ('nykaa', 'broader_fashion')),
            collection_mode TEXT NOT NULL CHECK(collection_mode IN ('automated', 'manual_unavailable')),
            description TEXT,
            last_success TEXT,
            last_error TEXT,
            updated_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at TEXT,
            raw_text TEXT NOT NULL,
            content_hash TEXT UNIQUE NOT NULL,
            source_scope TEXT NOT NULL CHECK(source_scope IN ('nykaa', 'broader_fashion')),
            ingested_at TEXT NOT NULL,
            run_id TEXT,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingest_logs (
            log_id TEXT PRIMARY KEY,
            run_id TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            attempted INTEGER NOT NULL,
            inserted INTEGER NOT NULL,
            skipped_duplicate INTEGER NOT NULL,
            failed_sources INTEGER NOT NULL,
            status TEXT NOT NULL,
            details TEXT
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phase1_source_id ON documents(source_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phase1_scope ON documents(source_scope);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phase1_hash ON documents(content_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phase1_ingested_at ON documents(ingested_at);")

    conn.commit()
    conn.close()


def compute_content_hash(text: str) -> str:
    """Computes deterministic SHA-256 hash of normalized text."""
    normalized = " ".join(text.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class Phase1DocumentStore:
    """Persistence repository for Phase 1 Ingestion."""

    @staticmethod
    def sync_sources(sources_list: List[Dict[str, Any]]):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        for src in sources_list:
            cursor.execute("""
                INSERT INTO sources (source_id, name, platform, source_type, source_scope, collection_mode, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    name = excluded.name,
                    platform = excluded.platform,
                    source_type = excluded.source_type,
                    source_scope = excluded.source_scope,
                    collection_mode = excluded.collection_mode,
                    description = excluded.description,
                    updated_at = excluded.updated_at;
            """, (
                src["source_id"],
                src["name"],
                src["platform"],
                src["source_type"],
                src["source_scope"],
                src["collection_mode"],
                src.get("description", ""),
                now
            ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_seen_hashes() -> Set[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content_hash FROM documents;")
        rows = cursor.fetchall()
        conn.close()
        return {r["content_hash"] for r in rows}

    @staticmethod
    def insert_documents(docs: List[Dict[str, Any]]) -> int:
        if not docs:
            return 0
        conn = get_db_connection()
        cursor = conn.cursor()
        inserted_count = 0

        for doc in docs:
            try:
                cursor.execute("""
                    INSERT INTO documents (
                        document_id, source_id, url, published_at, raw_text,
                        content_hash, source_scope, ingested_at, run_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc["document_id"],
                    doc["source_id"],
                    doc["url"],
                    doc.get("published_at"),
                    doc["raw_text"],
                    doc["content_hash"],
                    doc["source_scope"],
                    doc["ingested_at"],
                    doc.get("run_id")
                ))
                inserted_count += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        conn.close()
        return inserted_count

    @staticmethod
    def update_source_status(source_id: str, success: bool, error_message: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        if success:
            cursor.execute("UPDATE sources SET last_success = ?, last_error = NULL, updated_at = ? WHERE source_id = ?", (now, now, source_id))
        else:
            cursor.execute("UPDATE sources SET last_error = ?, updated_at = ? WHERE source_id = ?", (error_message, now, source_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM documents;")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as nykaa_count FROM documents WHERE source_scope = 'nykaa';")
        nykaa = cursor.fetchone()["nykaa_count"]

        cursor.execute("SELECT COUNT(*) as broader_count FROM documents WHERE source_scope = 'broader_fashion';")
        broader = cursor.fetchone()["broader_count"]

        cursor.execute("""
            SELECT s.source_id, s.name, s.platform, s.source_type, s.source_scope, s.collection_mode,
                   COUNT(d.document_id) as doc_count, s.last_success, s.last_error
            FROM sources s
            LEFT JOIN documents d ON s.source_id = d.source_id
            GROUP BY s.source_id;
        """)
        source_counts = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "total_documents": total,
            "nykaa_scope_count": nykaa,
            "broader_scope_count": broader,
            "by_source": source_counts
        }

    @staticmethod
    def list_documents(limit: int = 50, offset: int = 0, source_scope: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT d.document_id, d.source_id, s.name as source_name, s.platform, s.source_type,
                   d.url, d.published_at, d.raw_text, d.content_hash, d.source_scope, d.ingested_at
            FROM documents d
            JOIN sources s ON d.source_id = s.source_id
            WHERE 1=1
        """
        params = []
        if source_scope:
            query += " AND d.source_scope = ?"
            params.append(source_scope)
        if search:
            query += " AND d.raw_text LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY d.ingested_at DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor.execute(query, params)
        docs = [dict(r) for r in cursor.fetchall()]

        count_query = "SELECT COUNT(*) as total FROM documents d WHERE 1=1"
        count_params = []
        if source_scope:
            count_query += " AND d.source_scope = ?"
            count_params.append(source_scope)
        if search:
            count_query += " AND d.raw_text LIKE ?"
            count_params.append(f"%{search}%")

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()["total"]

        conn.close()
        return {"total": total_count, "limit": limit, "offset": offset, "documents": docs}
