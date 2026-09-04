import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

logger = logging.getLogger("phase3.vector_store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with WAL and Row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_vector_db():
    """Initializes schema for Phase 3 vector storage and indexing logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_vectors (
            chunk_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            vector BLOB NOT NULL,
            dim INTEGER NOT NULL,
            embedding_model TEXT NOT NULL,
            source_scope TEXT NOT NULL CHECK(source_scope IN ('nykaa', 'broader_fashion')),
            source_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            published_at TEXT,
            token_count INTEGER,
            indexed_at TEXT NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id)
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_scope ON chunk_vectors(source_scope);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_source ON chunk_vectors(source_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_type ON chunk_vectors(source_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_model ON chunk_vectors(embedding_model);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indexing_logs (
            log_id TEXT PRIMARY KEY,
            run_id TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            indexed_count INTEGER NOT NULL,
            total_vectors INTEGER NOT NULL,
            embedding_model TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT
        );
    """)

    conn.commit()
    conn.close()
    logger.info("Phase 3 vector database schema initialized.")


class VectorStore:
    """Repository for vector storage, metadata querying, and fast in-memory similarity matrix cache."""

    _cached_matrix: Optional[np.ndarray] = None
    _cached_metadata: Optional[List[Dict[str, Any]]] = None
    _cached_model: Optional[str] = None

    @classmethod
    def invalidate_cache(cls):
        cls._cached_matrix = None
        cls._cached_metadata = None
        cls._cached_model = None

    @staticmethod
    def get_indexed_chunk_ids(model_name: str) -> Set[str]:
        """Returns set of chunk_ids already indexed under the given embedding model."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT chunk_id FROM chunk_vectors WHERE embedding_model = ?", (model_name,))
        ids = {r[0] for r in cursor.fetchall()}
        conn.close()
        return ids

    @staticmethod
    def upsert_vectors(entries: List[Dict[str, Any]]) -> int:
        """Upserts a batch of vector records into SQLite."""
        if not entries:
            return 0
        conn = get_db_connection()
        cursor = conn.cursor()

        payload = []
        for e in entries:
            vec_bytes = e["vector"].astype(np.float32).tobytes() if isinstance(e["vector"], np.ndarray) else e["vector"]
            payload.append((
                e["chunk_id"],
                e["document_id"],
                vec_bytes,
                e["dim"],
                e["embedding_model"],
                e["source_scope"],
                e["source_id"],
                e["source_type"],
                e.get("published_at"),
                e.get("token_count", 0),
                e["indexed_at"]
            ))

        cursor.executemany("""
            INSERT OR REPLACE INTO chunk_vectors (
                chunk_id, document_id, vector, dim, embedding_model,
                source_scope, source_id, source_type, published_at,
                token_count, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payload)

        # Also update embedding_version on chunks table
        chunk_version_payload = [(e["embedding_model"], e["chunk_id"]) for e in entries]
        cursor.executemany("""
            UPDATE chunks SET embedding_version = ? WHERE chunk_id = ?
        """, chunk_version_payload)

        conn.commit()
        conn.close()
        VectorStore.invalidate_cache()
        return len(entries)

    @classmethod
    def load_index_into_memory(cls, model_name: str) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Loads all vectors and associated chunk + document metadata into memory for vector search.
        Caches the matrix in memory for sub-millisecond similarity scans.
        """
        if cls._cached_matrix is not None and cls._cached_model == model_name:
            return cls._cached_matrix, cls._cached_metadata

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                cv.chunk_id, cv.document_id, cv.vector, cv.dim, cv.embedding_model,
                cv.source_scope, cv.source_id, cv.source_type, cv.published_at, cv.token_count,
                c.text, d.url, d.raw_text, s.name as source_name, s.platform
            FROM chunk_vectors cv
            JOIN chunks c ON cv.chunk_id = c.chunk_id
            JOIN documents d ON cv.document_id = d.document_id
            JOIN sources s ON cv.source_id = s.source_id
            WHERE cv.embedding_model = ? AND d.relevance = 'relevant'
        """, (model_name,))

        rows = cursor.fetchall()

        # Automatic fallback: If requested model_name yields 0 rows, check actual embedding model indexed in DB
        if not rows:
            cursor.execute("SELECT cv.embedding_model FROM chunk_vectors cv LIMIT 1")
            existing_row = cursor.fetchone()
            if existing_row and existing_row[0]:
                actual_model = existing_row[0]
                cursor.execute("""
                    SELECT 
                        cv.chunk_id, cv.document_id, cv.vector, cv.dim, cv.embedding_model,
                        cv.source_scope, cv.source_id, cv.source_type, cv.published_at, cv.token_count,
                        c.text, d.url, d.raw_text, s.name as source_name, s.platform
                    FROM chunk_vectors cv
                    JOIN chunks c ON cv.chunk_id = c.chunk_id
                    JOIN documents d ON cv.document_id = d.document_id
                    JOIN sources s ON cv.source_id = s.source_id
                    WHERE cv.embedding_model = ? AND d.relevance = 'relevant'
                """, (actual_model,))
                rows = cursor.fetchall()
                model_name = actual_model

        conn.close()

        if not rows:
            cls._cached_matrix = np.empty((0, 384), dtype=np.float32)
            cls._cached_metadata = []
            cls._cached_model = model_name
            return cls._cached_matrix, cls._cached_metadata

        vectors = []
        metadata = []

        for r in rows:
            vec = np.frombuffer(r["vector"], dtype=np.float32)
            vectors.append(vec)
            metadata.append({
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "text": r["text"],
                "source_id": r["source_id"],
                "source_name": r["source_name"],
                "platform": r["platform"],
                "source_scope": r["source_scope"],
                "source_type": r["source_type"],
                "published_at": r["published_at"],
                "url": r["url"],
                "token_count": r["token_count"]
            })

        cls._cached_matrix = np.vstack(vectors)
        cls._cached_metadata = metadata
        cls._cached_model = model_name
        return cls._cached_matrix, cls._cached_metadata

    @staticmethod
    def get_vector_stats() -> Dict[str, Any]:
        """Returns statistical overview of the vector index."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT embedding_model) FROM chunk_vectors")
        total_vectors, model_count = cursor.fetchone()

        cursor.execute("""
            SELECT embedding_model, COUNT(*) as cnt, dim
            FROM chunk_vectors
            GROUP BY embedding_model
        """)
        models = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT source_scope, COUNT(*) as cnt
            FROM chunk_vectors
            GROUP BY source_scope
        """)
        by_scope = {r["source_scope"]: r["cnt"] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT s.source_id, s.name, COUNT(cv.chunk_id) as cnt
            FROM sources s
            LEFT JOIN chunk_vectors cv ON s.source_id = cv.source_id
            GROUP BY s.source_id
        """)
        by_source = [dict(r) for r in cursor.fetchall()]

        conn.close()

        return {
            "total_vectors": total_vectors,
            "models": models,
            "by_scope": by_scope,
            "by_source": by_source
        }

    @staticmethod
    def log_indexing_run(
        run_id: str,
        started_at: str,
        completed_at: str,
        indexed_count: int,
        total_vectors: int,
        embedding_model: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        log_id = f"idx_log_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO indexing_logs (
                log_id, run_id, started_at, completed_at, indexed_count,
                total_vectors, embedding_model, status, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, run_id, started_at, completed_at, indexed_count,
            total_vectors, embedding_model, status, json.dumps(details or {})
        ))
        conn.commit()
        conn.close()
        return log_id
