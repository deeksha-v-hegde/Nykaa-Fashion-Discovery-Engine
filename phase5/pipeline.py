import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from phase5.extractor import DocumentExtractor
from phase5.store import Phase5Store, get_db_connection, init_phase5_schema

logger = logging.getLogger("phase5.pipeline")


class ExtractionPipeline:
    """
    Phase 5 Extraction Pipeline Orchestrator.
    Iterates over relevant, canonical documents and extracts structured taxonomy fields.
    
    Ensures:
    - Incremental processing (skips already extracted documents).
    - Only relevant, non-duplicate documents are extracted.
    - Zero data loss, batch persistence.
    """

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.extractor = DocumentExtractor()

    def run_pipeline(self) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        run_id = f"ext_run_{start_time.strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"[{run_id}] Starting Phase 5 Structured Extraction pipeline pass...")

        init_phase5_schema()
        already_extracted = Phase5Store.get_extracted_doc_ids()

        # Fetch relevant canonical documents
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.document_id, d.cleaned_text, d.raw_text, s.source_scope
            FROM documents d
            JOIN sources s ON d.source_id = s.source_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL
            ORDER BY d.ingested_at ASC
        """)
        relevant_docs = [dict(r) for r in cursor.fetchall()]
        conn.close()

        total_relevant = len(relevant_docs)
        pending_docs = [d for d in relevant_docs if d["document_id"] not in already_extracted]

        logger.info(f"[{run_id}] Total relevant canonical documents: {total_relevant}. Pending extractions: {len(pending_docs)}")

        if not pending_docs:
            stats = Phase5Store.get_extraction_stats()
            return {
                "run_id": run_id,
                "status": "up_to_date",
                "total_relevant_documents": total_relevant,
                "newly_extracted": 0,
                "total_extractions": stats["total_extractions"],
                "stats": stats
            }

        # Process in batches
        newly_extracted_count = 0
        for i in range(0, len(pending_docs), self.batch_size):
            batch = pending_docs[i:i + self.batch_size]
            batch_payload = []

            for doc in batch:
                doc_text = doc["cleaned_text"] or doc["raw_text"] or ""
                extracted = self.extractor.extract_document(
                    doc_id=doc["document_id"],
                    text=doc_text,
                    source_scope=doc["source_scope"]
                )
                batch_payload.append(extracted.to_dict())

            saved = Phase5Store.save_extractions(batch_payload)
            newly_extracted_count += saved
            logger.info(f"[{run_id}] Extracted {newly_extracted_count}/{len(pending_docs)} documents...")

        end_time = datetime.now(timezone.utc)
        stats = Phase5Store.get_extraction_stats()

        logger.info(f"[{run_id}] Structured Extraction completed. Total extractions in DB: {stats['total_extractions']}")

        return {
            "run_id": run_id,
            "status": "completed",
            "total_relevant_documents": total_relevant,
            "newly_extracted": newly_extracted_count,
            "total_extractions": stats["total_extractions"],
            "duration_seconds": (end_time - start_time).total_seconds(),
            "stats": stats
        }
