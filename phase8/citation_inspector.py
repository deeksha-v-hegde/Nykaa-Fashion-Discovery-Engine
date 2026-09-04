import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional
from phase8.models import CitationDetailPayload

logger = logging.getLogger("phase8.citation_inspector")
DB_PATH = Path("data/discovery_engine.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


class CitationInspector:
    """
    Phase 8 Citation Inspector.
    Resolves any claim or chunk ID to its exact raw source evidence provenance.
    """

    @staticmethod
    def get_citation_detail(chunk_id: str) -> Optional[CitationDetailPayload]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                c.chunk_id, c.document_id, c.text as chunk_text,
                d.cleaned_text, d.raw_text, d.url, d.published_at, d.relevance, d.duplicate_of,
                s.source_id, s.name as source_name, s.platform, s.source_scope, s.source_type
            FROM chunks c
            JOIN documents d ON c.document_id = d.document_id
            JOIN sources s ON c.source_id = s.source_id
            WHERE c.chunk_id = ?
        """, (chunk_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        r = dict(row)
        return CitationDetailPayload(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            source_id=r["source_id"],
            source_name=r["source_name"],
            platform=r["platform"],
            source_scope=r["source_scope"],
            source_type=r["source_type"],
            published_at=r["published_at"],
            url=r["url"] or "",
            chunk_text=r["chunk_text"],
            cleaned_text=r["cleaned_text"] or r["chunk_text"],
            raw_text=r["raw_text"] or r["chunk_text"],
            relevance=r["relevance"] or "relevant",
            duplicate_of=r["duplicate_of"]
        )
