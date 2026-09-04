import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from phase2.chunker import DocumentChunker
from phase2.classifier import RelevanceClassifier
from phase2.deduper import NearDuplicateDetector
from phase2.normalizer import TextNormalizer
from phase2.store import Phase2Store, init_phase2_db

logger = logging.getLogger("phase2.pipeline")


class Phase2Pipeline:
    """
    Phase 2 Orchestrator: Cleaning, Deduplication, Relevance Classification, and Chunking.
    Produces clean, relevant, chunked corpus records ready for Phase 3 vector embeddings.
    """

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.deduper = NearDuplicateDetector(jaccard_threshold=0.85)

    def run(self) -> Dict[str, Any]:
        """
        Executes the Phase 2 cleaning and chunking pipeline across all ingested documents.
        """
        start_time = datetime.now(timezone.utc)
        run_id = f"phase2_run_{start_time.strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"[{run_id}] Starting Phase 2 Pipeline execution...")

        # 1. Initialize schema
        init_phase2_db()

        # 2. Fetch all ingested documents
        raw_documents = Phase2Store.get_all_documents_for_cleaning()
        total_docs = len(raw_documents)
        logger.info(f"[{run_id}] Retrieved {total_docs} raw documents for processing.")

        doc_updates: List[Dict[str, Any]] = []
        all_chunks: List[Dict[str, Any]] = []

        cleaned_count = 0
        duplicates_flagged = 0
        relevant_count = 0
        not_relevant_count = 0
        unknown_count = 0

        now_iso = datetime.now(timezone.utc).isoformat()

        # 3. Process each document
        for doc in raw_documents:
            doc_id = doc["document_id"]
            raw_text = doc["raw_text"]
            source_scope = doc["source_scope"]
            source_id = doc["source_id"]

            # Step 3a: Normalize text
            cleaned_text = TextNormalizer.normalize(raw_text)
            if cleaned_text:
                cleaned_count += 1

            # Step 3b: Deduplication / Near-duplicate check
            duplicate_of = self.deduper.check_and_register(doc_id, cleaned_text)
            if duplicate_of:
                duplicates_flagged += 1

            # Step 3c: Relevance Classification
            relevance, reason, matched_facets = RelevanceClassifier.classify(cleaned_text, source_scope)

            # If it is a duplicate, record duplicate trail in reason
            if duplicate_of:
                reason = f"[Near-Duplicate of {duplicate_of}] {reason}"

            if relevance == "relevant":
                relevant_count += 1
            elif relevance == "not_relevant":
                not_relevant_count += 1
            else:
                unknown_count += 1

            doc_updates.append({
                "document_id": doc_id,
                "cleaned_text": cleaned_text,
                "relevance": relevance,
                "relevance_reason": reason,
                "duplicate_of": duplicate_of,
                "cleaned_at": now_iso
            })

            # Step 3d: Chunking (only relevant, non-duplicate documents form the default retrieval corpus)
            if relevance == "relevant" and not duplicate_of:
                draft_chunks = self.chunker.chunk_document(
                    document_id=doc_id,
                    cleaned_text=cleaned_text,
                    source_scope=source_scope,
                    source_id=source_id
                )
                for chk in draft_chunks:
                    all_chunks.append({
                        "chunk_id": chk.chunk_id,
                        "document_id": chk.document_id,
                        "ordinal": chk.ordinal,
                        "text": chk.text,
                        "token_count": chk.token_count,
                        "source_scope": chk.source_scope,
                        "source_id": chk.source_id,
                        "embedding_version": None,
                        "created_at": now_iso
                    })

        # 4. Persist document updates and chunks
        logger.info(f"[{run_id}] Updating {len(doc_updates)} documents in store...")
        Phase2Store.batch_update_document_cleaning(doc_updates)

        logger.info(f"[{run_id}] Replacing chunks table with {len(all_chunks)} newly generated chunks...")
        chunks_inserted = Phase2Store.replace_chunks_for_run(all_chunks)

        end_time = datetime.now(timezone.utc)
        completed_iso = end_time.isoformat()

        # 5. Log cleaning run
        details = {
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.chunk_overlap,
            "duration_seconds": (end_time - start_time).total_seconds()
        }
        Phase2Store.log_cleaning_run(
            run_id=run_id,
            started_at=start_time.isoformat(),
            completed_at=completed_iso,
            total_documents=total_docs,
            cleaned_count=cleaned_count,
            duplicates_flagged=duplicates_flagged,
            relevant_count=relevant_count,
            not_relevant_count=not_relevant_count,
            unknown_count=unknown_count,
            chunks_created=chunks_inserted,
            status="completed",
            details=details
        )

        stats = Phase2Store.get_phase2_stats()
        logger.info(f"[{run_id}] Phase 2 Pipeline finished successfully. Chunks created: {chunks_inserted}")
        return {
            "run_id": run_id,
            "status": "completed",
            "total_documents": total_docs,
            "cleaned_count": cleaned_count,
            "duplicates_flagged": duplicates_flagged,
            "relevant_count": relevant_count,
            "not_relevant_count": not_relevant_count,
            "unknown_count": unknown_count,
            "chunks_created": chunks_inserted,
            "stats": stats
        }
