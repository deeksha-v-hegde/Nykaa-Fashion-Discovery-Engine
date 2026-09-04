import sqlite3
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    """Initializes the database schema for Phase 1 (and future phase tables)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sources Table
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

    # Documents Table (Phase 1 Data Contract)
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

    # Ingest Runs Log Table
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

    # Create Indexes for high-performance lookup and deduplication
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source_id ON documents(source_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_scope ON documents(source_scope);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_ingested_at ON documents(ingested_at);")

    conn.commit()
    conn.close()
    logger.info("Database initialized with Phase 1 tables.")


def compute_content_hash(text: str) -> str:
    """Computes deterministic SHA-256 hash of normalized text."""
    normalized = " ".join(text.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class DocumentStore:
    """Repository class for querying and storing documents and sources."""

    @staticmethod
    def sync_sources_from_registry(sources_list: List[Dict[str, Any]]):
        """Syncs sources from sources.yaml into SQLite database."""
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
        """Returns set of all SHA-256 hashes currently stored in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content_hash FROM documents;")
        rows = cursor.fetchall()
        conn.close()
        return {r["content_hash"] for r in rows}

    @staticmethod
    def insert_documents(docs: List[Dict[str, Any]]) -> int:
        """
        Inserts new documents, skipping duplicate content hashes.
        Returns count of successfully inserted documents.
        """
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
                # Duplicate content_hash encountered
                pass

        conn.commit()
        conn.close()
        return inserted_count

    @staticmethod
    def update_source_status(source_id: str, success: bool, error_message: Optional[str] = None):
        """Updates last_success or last_error for a source."""
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        if success:
            cursor.execute("""
                UPDATE sources SET last_success = ?, last_error = NULL, updated_at = ? WHERE source_id = ?
            """, (now, now, source_id))
        else:
            cursor.execute("""
                UPDATE sources SET last_error = ?, updated_at = ? WHERE source_id = ?
            """, (error_message, now, source_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_document_counts() -> Dict[str, Any]:
        """Returns document summary counts."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM documents;")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as nykaa_count FROM documents WHERE source_scope = 'nykaa';")
        nykaa = cursor.fetchone()["nykaa_count"]

        cursor.execute("SELECT COUNT(*) as broader_count FROM documents WHERE source_scope = 'broader_fashion';")
        broader = cursor.fetchone()["broader_count"]

        cursor.execute("""
            SELECT s.platform, s.source_type, s.source_scope, COUNT(d.document_id) as doc_count
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
    def list_documents(
        limit: int = 50,
        offset: int = 0,
        source_scope: Optional[str] = None,
        source_id: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lists documents with pagination and metadata."""
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

        if source_id:
            query += " AND d.source_id = ?"
            params.append(source_id)

        if search_query:
            query += " AND d.raw_text LIKE ?"
            params.append(f"%{search_query}%")

        query += " ORDER BY d.ingested_at DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor.execute(query, params)
        docs = [dict(r) for r in cursor.fetchall()]

        # Total matching count
        count_query = "SELECT COUNT(*) as total FROM documents d WHERE 1=1"
        count_params = []
        if source_scope:
            count_query += " AND d.source_scope = ?"
            count_params.append(source_scope)
        if source_id:
            count_query += " AND d.source_id = ?"
            count_params.append(source_id)
        if search_query:
            count_query += " AND d.raw_text LIKE ?"
            count_params.append(f"%{search_query}%")

        cursor.execute(count_query, count_params)
        total_matching = cursor.fetchone()["total"]

        conn.close()
        return {
            "total": total_matching,
            "limit": limit,
            "offset": offset,
            "documents": docs
        }
