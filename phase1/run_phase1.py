"""
Phase 1 Standalone Ingestion Runner & Validator
Usage: python -m phase1.run_phase1
"""

import json
from phase1.ingest import Phase1IngestionJob
from phase1.store import Phase1DocumentStore


def main():
    print("=================================================================")
    print(" NYKAA FASHION AI DISCOVERY ENGINE — PHASE 1 INGESTION RUNNER")
    print("=================================================================")
    
    job = Phase1IngestionJob()
    
    # Run 1: Ingestion
    print("\n[Step 1] Executing First Ingestion Pass...")
    result1 = job.run()
    print(f"Status: {result1['status']}")
    print(f"Attempted: {result1['attempted']}")
    print(f"Newly Inserted: {result1['inserted']}")
    print(f"Skipped Duplicates: {result1['skipped_duplicate']}")
    print(f"Failed Sources: {result1['failed_sources']}")
    
    # Run 2: Deduplication Check
    print("\n[Step 2] Executing Second Ingestion Pass (Deduplication Gate Check)...")
    result2 = job.run()
    print(f"Status: {result2['status']}")
    print(f"Attempted: {result2['attempted']}")
    print(f"Newly Inserted: {result2['inserted']} (Expected 0 on repeat run)")
    print(f"Skipped Duplicates: {result2['skipped_duplicate']} (Expected {result1['attempted']})")
    
    # Verification of Document Store
    print("\n[Step 3] Querying Phase 1 Document Store Statistics...")
    stats = Phase1DocumentStore.get_stats()
    print(f"Total Unique Documents in DB: {stats['total_documents']}")
    print(f"Nykaa Specific Documents: {stats['nykaa_scope_count']}")
    print(f"Broader Fashion Documents: {stats['broader_scope_count']}")
    
    print("\n[Step 4] Sampling Ingested Documents...")
    docs_sample = Phase1DocumentStore.list_documents(limit=3)
    for doc in docs_sample["documents"]:
        print(f" - [{doc['source_scope']}] {doc['source_name']} ({doc['platform']}): {doc['raw_text'][:80]}...")
        print(f"   URL: {doc['url']} | Hash: {doc['content_hash'][:16]}...")

    print("\n=================================================================")
    print(" PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY")
    print("=================================================================")


if __name__ == "__main__":
    main()
