import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.settings import Settings
from phase3.embedder import TextEmbedder
from phase3.vector_store import VectorStore, get_db_connection, init_vector_db

logger = logging.getLogger("phase3.indexer")


class VectorIndexer:
    """
    Phase 3 Vector Indexer.
    Incrementally indexes retrieval chunks into the vector database.
    
    Principles (Architecture Guideline):
    - Embeds only chunks where `embedding_version` is NULL or != current `EMBEDDING_MODEL`.
    - Does NOT re-embed the entire corpus unless the model version has changed.
    - Encodes vectors in batches with progress logging.
    - Stores complete filter metadata alongside vectors.
    """

    def __init__(self, embedding_model: Optional[str] = None, batch_size: int = 128):
        settings = Settings()
        self.embedding_model = embedding_model or settings.embedding_model or "tfidf-lsa-384"
        self.batch_size = batch_size
        self.embedder = TextEmbedder(model_name=self.embedding_model)

    def run_indexing(self) -> Dict[str, Any]:
        """
        Executes incremental indexing pass over unindexed or version-mismatched chunks.
        """
        start_time = datetime.now(timezone.utc)
        run_id = f"index_run_{start_time.strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"[{run_id}] Starting Vector Indexing pass for model '{self.embedding_model}'...")

        # 1. Ensure DB schema exists
        init_vector_db()

        # 2. Fetch pending chunks
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.chunk_id, c.document_id, c.ordinal, c.text, c.token_count,
                c.source_scope, c.source_id, c.embedding_version,
                d.published_at, s.source_type
            FROM chunks c
            JOIN documents d ON c.document_id = d.document_id
            JOIN sources s ON c.source_id = s.source_id
            WHERE c.embedding_version IS NULL OR c.embedding_version != ?
            ORDER BY c.created_at ASC
        """, (self.embedding_model,))

        pending_chunks = [dict(r) for r in cursor.fetchall()]

        # Also get total corpus chunks count
        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_corpus_chunks = cursor.fetchone()[0]
        conn.close()

        logger.info(f"[{run_id}] Found {len(pending_chunks)} pending chunks to index (out of {total_corpus_chunks} total chunks).")

        if not pending_chunks:
            logger.info(f"[{run_id}] All {total_corpus_chunks} chunks already indexed under model '{self.embedding_model}'.")
            stats = VectorStore.get_vector_stats()
            return {
                "run_id": run_id,
                "status": "up_to_date",
                "embedding_model": self.embedding_model,
                "newly_indexed": 0,
                "total_chunks": total_corpus_chunks,
                "total_vectors": stats["total_vectors"],
                "stats": stats
            }

        # 3. If embedder not fitted yet, fit on corpus text
        if not self.embedder._is_fitted:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM chunks")
            all_texts = [r[0] for r in cursor.fetchall()]
            conn.close()
            self.embedder.fit(all_texts)

        # 4. Batch encoding and persistence
        now_iso = datetime.now(timezone.utc).isoformat()
        indexed_count = 0

        for i in range(0, len(pending_chunks), self.batch_size):
            batch = pending_chunks[i:i + self.batch_size]
            batch_texts = [c["text"] for c in batch]

            # Generate vectors
            batch_vectors = self.embedder.embed_texts(batch_texts)

            # Build entries
            entries = []
            for j, c in enumerate(batch):
                entries.append({
                    "chunk_id": c["chunk_id"],
                    "document_id": c["document_id"],
                    "vector": batch_vectors[j],
                    "dim": self.embedder.dim,
                    "embedding_model": self.embedding_model,
                    "source_scope": c["source_scope"],
                    "source_id": c["source_id"],
                    "source_type": c["source_type"],
                    "published_at": c.get("published_at"),
                    "token_count": c.get("token_count", 0),
                    "indexed_at": now_iso
                })

            # Upsert
            upserted = VectorStore.upsert_vectors(entries)
            indexed_count += upserted
            logger.info(f"[{run_id}] Indexed {indexed_count}/{len(pending_chunks)} chunks...")

        end_time = datetime.now(timezone.utc)
        stats = VectorStore.get_vector_stats()

        # 5. Log run
        VectorStore.log_indexing_run(
            run_id=run_id,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            indexed_count=indexed_count,
            total_vectors=stats["total_vectors"],
            embedding_model=self.embedding_model,
            status="completed",
            details={
                "dim": self.embedder.dim,
                "batch_size": self.batch_size,
                "duration_seconds": (end_time - start_time).total_seconds()
            }
        )

        logger.info(f"[{run_id}] Indexing completed successfully. Total vectors in index: {stats['total_vectors']}")
        return {
            "run_id": run_id,
            "status": "completed",
            "embedding_model": self.embedding_model,
            "newly_indexed": indexed_count,
            "total_chunks": total_corpus_chunks,
            "total_vectors": stats["total_vectors"],
            "stats": stats
        }
