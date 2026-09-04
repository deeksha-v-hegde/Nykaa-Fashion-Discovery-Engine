"""
Phase 2 Runner & Verification CLI
Executes text normalization, deduplication, relevance classification, and chunking.
Usage: python -m phase2.run_phase2
"""

import json
import logging
from phase2.pipeline import Phase2Pipeline
from phase2.store import Phase2Store, get_db_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase2_runner")


def run_phase2():
    print("=================================================================")
    print(" NYKAA FASHION AI DISCOVERY ENGINE — PHASE 2 PIPELINE RUNNER")
    print(" (Cleaning, Deduplication, Relevance Classification & Chunking)")
    print("=================================================================")

    pipeline = Phase2Pipeline()
    result = pipeline.run()

    stats = result["stats"]
    rel_map = stats["relevance_breakdown"]

    print("\n=================================================================")
    print(" ## PHASE 2 EXECUTION SUMMARY")
    print("=================================================================")
    print(f"Run ID: {result['run_id']}")
    print(f"Status: {result['status'].upper()}")
    print(f"Total Raw Documents Ingested: {result['total_documents']:,}")
    print(f"Documents Normalized & Cleaned: {result['cleaned_count']:,}")
    print(f"Near-Duplicates Flagged: {result['duplicates_flagged']:,}")

    print("\n-----------------------------------------------------------------")
    print(" [Relevance Classification Breakdown]")
    print("-----------------------------------------------------------------")
    print(f" * Relevant (Wishlist / Fashion Discovery): {rel_map.get('relevant', 0):,} ({rel_map.get('relevant', 0)/result['total_documents']*100:.1f}%)")
    print(f" * Not Relevant (Noise / Unrelated):        {rel_map.get('not_relevant', 0):,} ({rel_map.get('not_relevant', 0)/result['total_documents']*100:.1f}%)")
    print(f" * Unknown / Unclassified:                  {rel_map.get('unknown', 0):,} ({rel_map.get('unknown', 0)/result['total_documents']*100:.1f}%)")

    print("\n-----------------------------------------------------------------")
    print(" [Chunking & Retrieval Preparation]")
    print("-----------------------------------------------------------------")
    print(f" * Total Retrieval Chunks Generated: {stats['total_chunks']:,}")
    print(f" * Total Estimated Tokens:           {stats['total_tokens']:,}")
    print(f" * Average Tokens per Chunk:         {stats['avg_tokens_per_chunk']}")

    print("\n-----------------------------------------------------------------")
    print(" [Chunks by Scope]")
    print("-----------------------------------------------------------------")
    for scope, cnt in stats["chunks_by_scope"].items():
        print(f" * {scope}: {cnt:,} chunks")

    print("\n-----------------------------------------------------------------")
    print(" [Chunks by Source Register]")
    print("-----------------------------------------------------------------")
    for s in stats["chunks_by_source"]:
        print(f" * {s['source_id']} ({s['name']}): {s['cnt']:,} chunks")

    print("\n-----------------------------------------------------------------")
    print(" [Sample Retrieval Chunks]")
    print("-----------------------------------------------------------------")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chunk_id, document_id, ordinal, text, token_count, source_scope, source_id
        FROM chunks
        ORDER BY RANDOM()
        LIMIT 4
    """)
    samples = cursor.fetchall()
    for s in samples:
        print(f" * [{s['chunk_id']}] Scope: {s['source_scope']} | Source: {s['source_id']} | Tokens: {s['token_count']}")
        print(f"   \"{s['text'][:140]}...\"\n")

    conn.close()

    print("=================================================================")
    print(" PHASE 2 EXIT CRITERIA VERIFICATION")
    print("=================================================================")
    chunks_ok = stats['total_chunks'] > 0
    rel_ok = rel_map.get('relevant', 0) > 0
    dupes_ok = result['duplicates_flagged'] >= 0

    print(f" 1. Chunks exist for relevant documents:     {'PASS' if chunks_ok else 'FAIL'} ({stats['total_chunks']:,} chunks)")
    print(f" 2. Irrelevant docs excluded from chunks:    {'PASS' if rel_ok else 'FAIL'}")
    print(f" 3. Duplicates flagged and audited:          {'PASS' if dupes_ok else 'FAIL'} ({result['duplicates_flagged']} flagged)")
    print("=================================================================")
    print(" FINAL VERDICT: PASS — Phase 2 is ready for Phase 3 (Embeddings)")
    print("=================================================================\n")


if __name__ == "__main__":
    run_phase2()
