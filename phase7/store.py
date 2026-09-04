import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("phase7.store")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_phase7_schema():
    """Initializes schema for Phase 7 opportunities and snapshots."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            opportunity_count INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            opportunity_id TEXT PRIMARY KEY,
            rank INTEGER NOT NULL,
            title TEXT NOT NULL,
            rank_label TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('validate_next', 'under_investigation', 'validated')),
            user_job TEXT NOT NULL,
            blocker TEXT NOT NULL,
            current_workaround TEXT NOT NULL,
            non_monetary_intervention_type TEXT NOT NULL,
            scale_mention_count INTEGER NOT NULL,
            scale_share_pct REAL NOT NULL,
            sample_size_n INTEGER NOT NULL,
            confidence TEXT NOT NULL,
            evidence_gap TEXT NOT NULL,
            research_hypothesis TEXT NOT NULL,
            research_prioritisation_score REAL NOT NULL,
            card_json TEXT NOT NULL,
            snapshot_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (snapshot_id) REFERENCES opportunity_snapshots(snapshot_id)
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_rank ON opportunities(rank);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_score ON opportunities(research_prioritisation_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_snapshot ON opportunities(snapshot_id);")

    conn.commit()
    conn.close()
    logger.info("Phase 7 opportunities database schema initialized.")


class Phase7Store:
    """Repository for persisting ranked opportunity cards and snapshots."""

    @staticmethod
    def save_opportunity_snapshot(opportunity_cards: List[Dict[str, Any]]) -> str:
        init_phase7_schema()
        sid = f"opp_snap_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO opportunity_snapshots (snapshot_id, opportunity_count, created_at)
            VALUES (?, ?, ?)
        """, (sid, len(opportunity_cards), now_iso))

        payload = []
        for card in opportunity_cards:
            card["snapshot_id"] = sid
            payload.append((
                card["opportunity_id"],
                card["rank"],
                card["title"],
                card["rank_label"],
                card.get("status", "validate_next"),
                card["user_job"],
                card["blocker"],
                card["current_workaround"],
                card["non_monetary_intervention_type"],
                card["scale_mention_count"],
                card["scale_share_pct"],
                card.get("sample_size_n", 1151),
                card["confidence"],
                card["evidence_gap"],
                card["research_hypothesis"],
                card["scoring"]["research_prioritisation_score"],
                json.dumps(card),
                sid,
                now_iso
            ))

        cursor.executemany("""
            INSERT OR REPLACE INTO opportunities (
                opportunity_id, rank, title, rank_label, status, user_job, blocker,
                current_workaround, non_monetary_intervention_type, scale_mention_count,
                scale_share_pct, sample_size_n, confidence, evidence_gap,
                research_hypothesis, research_prioritisation_score, card_json,
                snapshot_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payload)

        conn.commit()
        conn.close()
        return sid

    @staticmethod
    def get_latest_opportunities() -> List[Dict[str, Any]]:
        init_phase7_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT card_json FROM opportunities
            WHERE snapshot_id = (SELECT snapshot_id FROM opportunity_snapshots ORDER BY created_at DESC LIMIT 1)
            ORDER BY rank ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [json.loads(r["card_json"]) for r in rows]

    @staticmethod
    def get_opportunity_by_id(opp_id: str) -> Optional[Dict[str, Any]]:
        init_phase7_schema()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT card_json FROM opportunities WHERE opportunity_id = ? ORDER BY created_at DESC LIMIT 1", (opp_id,))
        row = cursor.fetchone()
        conn.close()
        return json.loads(row["card_json"]) if row else None
