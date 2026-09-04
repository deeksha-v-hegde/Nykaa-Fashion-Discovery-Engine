import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("phase5.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase5_schema():
    """Initializes schema for Phase 5 document extractions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_extractions (
            document_id TEXT PRIMARY KEY,
            product_category TEXT,
            user_behaviour TEXT,
            wishlist_behaviour TEXT,
            purchase_intent TEXT,
            purchase_stage TEXT,
            barrier TEXT,
            uncertainty TEXT,
            user_job TEXT,
            workaround TEXT,
            external_information_source TEXT,
            alternative_considered TEXT,
            occasion TEXT,
            fit_size TEXT,
            styling TEXT,
            price TEXT,
            reviews_social_validation TEXT,
            availability TEXT,
            quality_expectation TEXT,
            other_new_theme TEXT,
            evidence_strength TEXT NOT NULL CHECK(evidence_strength IN ('high', 'medium', 'low')),
            extracted_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(document_id)
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_barrier ON document_extractions(barrier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_wishlist ON document_extractions(wishlist_behaviour);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_strength ON document_extractions(evidence_strength);")

    conn.commit()
    conn.close()
    logger.info("Phase 5 document_extractions schema initialized.")


class Phase5Store:
    """Repository for managing structured document extractions."""

    @staticmethod
    def get_extracted_doc_ids() -> Set[str]:
        """Returns set of document_ids already extracted."""
        init_phase5_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT document_id FROM document_extractions")
        ids = {r[0] for r in cursor.fetchall()}
        conn.close()
        return ids

    @staticmethod
    def save_extractions(extractions: List[Dict[str, Any]]) -> int:
        """Upserts a batch of document extraction records."""
        if not extractions:
            return 0

        init_phase5_schema()
        conn = get_db_connection()
        cursor = conn.cursor()

        payload = [
            (
                e["document_id"],
                e.get("product_category"),
                e.get("user_behaviour"),
                e.get("wishlist_behaviour"),
                e.get("purchase_intent"),
                e.get("purchase_stage"),
                e.get("barrier"),
                e.get("uncertainty"),
                e.get("user_job"),
                e.get("workaround"),
                e.get("external_information_source"),
                e.get("alternative_considered"),
                e.get("occasion"),
                e.get("fit_size"),
                e.get("styling"),
                e.get("price"),
                e.get("reviews_social_validation"),
                e.get("availability"),
                e.get("quality_expectation"),
                e.get("other_new_theme"),
                e.get("evidence_strength", "medium"),
                e.get("extracted_at", datetime.now(timezone.utc).isoformat())
            )
            for e in extractions
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO document_extractions (
                document_id, product_category, user_behaviour, wishlist_behaviour,
                purchase_intent, purchase_stage, barrier, uncertainty, user_job,
                workaround, external_information_source, alternative_considered,
                occasion, fit_size, styling, price, reviews_social_validation,
                availability, quality_expectation, other_new_theme,
                evidence_strength, extracted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payload)

        conn.commit()
        conn.close()
        return len(extractions)

    @staticmethod
    def get_extraction_stats() -> Dict[str, Any]:
        """Computes statistical overview of extractions for Phase 5 verification."""
        init_phase5_schema()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM document_extractions")
        total_extractions = cursor.fetchone()[0]

        cursor.execute("""
            SELECT barrier, COUNT(*) as cnt
            FROM document_extractions
            WHERE barrier IS NOT NULL
            GROUP BY barrier
            ORDER BY cnt DESC
        """)
        by_barrier = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT wishlist_behaviour, COUNT(*) as cnt
            FROM document_extractions
            WHERE wishlist_behaviour IS NOT NULL
            GROUP BY wishlist_behaviour
            ORDER BY cnt DESC
        """)
        by_wishlist = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT evidence_strength, COUNT(*) as cnt
            FROM document_extractions
            GROUP BY evidence_strength
        """)
        by_strength = {r["evidence_strength"]: r["cnt"] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT COUNT(*) FROM document_extractions
            WHERE other_new_theme IS NOT NULL
        """)
        emerging_count = cursor.fetchone()[0]

        conn.close()

        return {
            "total_extractions": total_extractions,
            "by_barrier": by_barrier,
            "by_wishlist": by_wishlist,
            "by_strength": by_strength,
            "emerging_count": emerging_count
        }

    @staticmethod
    def get_extractions(limit: int = 50) -> List[Dict[str, Any]]:
        init_phase5_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM document_extractions ORDER BY extracted_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
