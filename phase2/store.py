import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("phase2.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with WAL and Row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase2_db():
    """Initializes schema migrations and tables for Phase 2."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Check and add Phase 2 columns to documents table
    cursor.execute("PRAGMA table_info(documents);")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    phase2_columns = [
        ("cleaned_text", "TEXT"),
        ("relevance", "TEXT CHECK(relevance IN ('relevant', 'not_relevant', 'unknown'))"),
        ("relevance_reason", "TEXT"),
        ("duplicate_of", "TEXT"),
        ("cleaned_at", "TEXT")
    ]

    for col_name, col_type in phase2_columns:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type};")
            logger.info(f"Added column '{col_name}' to documents table.")

    # 2. Create chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            ordinal INTEGER NOT NULL,
            text TEXT NOT NULL,
            token_count INTEGER NOT NULL,
            source_scope TEXT NOT NULL CHECK(source_scope IN ('nykaa', 'broader_fashion')),
            source_id TEXT NOT NULL,
            embedding_version TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(document_id)
        );
    """)

    # Indices on chunks for high-speed retrieval and scoping
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(document_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_scope ON chunks(source_scope);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);")

    # 3. Create cleaning_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cleaning_logs (
            log_id TEXT PRIMARY KEY,
            run_id TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            total_documents INTEGER NOT NULL,
            cleaned_count INTEGER NOT NULL,
            duplicates_flagged INTEGER NOT NULL,
            relevant_count INTEGER NOT NULL,
            not_relevant_count INTEGER NOT NULL,
            unknown_count INTEGER NOT NULL,
            chunks_created INTEGER NOT NULL,
            status TEXT NOT NULL,
            details TEXT
        );
    """)

    conn.commit()
    conn.close()
    logger.info("Phase 2 database schema initialized.")


class Phase2Store:
    """Repository methods for Phase 2 data persistence."""

    @staticmethod
    def get_all_documents_for_cleaning() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT document_id, source_id, url, published_at, raw_text, source_scope, duplicate_of
            FROM documents
            ORDER BY ingested_at ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def batch_update_document_cleaning(updates: List[Dict[str, Any]]) -> int:
        if not updates:
            return 0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executemany("""
            UPDATE documents
            SET cleaned_text = :cleaned_text,
                relevance = :relevance,
                relevance_reason = :relevance_reason,
                duplicate_of = :duplicate_of,
                cleaned_at = :cleaned_at
            WHERE document_id = :document_id
        """, updates)
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        return updated

    @staticmethod
    def replace_chunks_for_run(chunks: List[Dict[str, Any]]) -> int:
        """Atomically clears and replaces chunks."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks;")
        if chunks:
            cursor.executemany("""
                INSERT INTO chunks (
                    chunk_id, document_id, ordinal, text, token_count,
                    source_scope, source_id, embedding_version, created_at
                ) VALUES (
                    :chunk_id, :document_id, :ordinal, :text, :token_count,
                    :source_scope, :source_id, :embedding_version, :created_at
                )
            """, chunks)
        inserted = len(chunks)
        conn.commit()
        conn.close()
        return inserted

    @staticmethod
    def log_cleaning_run(
        run_id: str,
        started_at: str,
        completed_at: str,
        total_documents: int,
        cleaned_count: int,
        duplicates_flagged: int,
        relevant_count: int,
        not_relevant_count: int,
        unknown_count: int,
        chunks_created: int,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        log_id = f"clean_log_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO cleaning_logs (
                log_id, run_id, started_at, completed_at, total_documents,
                cleaned_count, duplicates_flagged, relevant_count, not_relevant_count,
                unknown_count, chunks_created, status, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, run_id, started_at, completed_at, total_documents,
            cleaned_count, duplicates_flagged, relevant_count, not_relevant_count,
            unknown_count, chunks_created, status, json.dumps(details or {})
        ))
        conn.commit()
        conn.close()
        return log_id

    @staticmethod
    def get_phase2_stats() -> Dict[str, Any]:
        """Returns statistical overview of Phase 2 cleaning and chunking."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Documents by relevance
        cursor.execute("""
            SELECT COALESCE(relevance, 'unprocessed') as rel, COUNT(*) as cnt
            FROM documents
            GROUP BY rel
        """)
        relevance_counts = {r["rel"]: r["cnt"] for r in cursor.fetchall()}

        # Duplicates count
        cursor.execute("SELECT COUNT(*) FROM documents WHERE duplicate_of IS NOT NULL")
        duplicates_count = cursor.fetchone()[0]

        # Total chunks count and tokens
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(token_count), 0), COALESCE(AVG(token_count), 0) FROM chunks")
        total_chunks, total_tokens, avg_tokens = cursor.fetchone()

        # Chunks by source scope
        cursor.execute("""
            SELECT source_scope, COUNT(*) as cnt
            FROM chunks
            GROUP BY source_scope
        """)
        chunks_by_scope = {r["source_scope"]: r["cnt"] for r in cursor.fetchall()}

        # Chunks by source id
        cursor.execute("""
            SELECT s.source_id, s.name, COUNT(c.chunk_id) as cnt
            FROM sources s
            LEFT JOIN chunks c ON s.source_id = c.source_id
            GROUP BY s.source_id
        """)
        chunks_by_source = [dict(r) for r in cursor.fetchall()]

        conn.close()

        return {
            "relevance_breakdown": relevance_counts,
            "duplicates_flagged": duplicates_count,
            "total_chunks": total_chunks,
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": round(avg_tokens, 1) if avg_tokens else 0,
            "chunks_by_scope": chunks_by_scope,
            "chunks_by_source": chunks_by_source
        }
