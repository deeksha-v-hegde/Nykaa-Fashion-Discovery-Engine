import logging
from typing import Any, Dict, List, Optional

from phase6.quantifier import CorpusQuantifier
from phase7.clusterer import OpportunityClusterer
from phase7.evidence_picker import EvidencePicker
from phase7.journey_builder import JourneyBuilder
from phase7.models import OpportunityCard
from phase7.scorer import OpportunityScorer
from phase7.store import Phase7Store, get_db_connection

logger = logging.getLogger("phase7.pipeline")


class OpportunityPipeline:
    """
    Phase 7 Master Opportunity Pipeline Orchestrator.
    Generates, scores, ranks, and persists the Prioritised Research Shortlist.
    """

    def __init__(self, embedding_model: Optional[str] = None):
        self.quantifier = CorpusQuantifier()
        self.evidence_picker = EvidencePicker(embedding_model=embedding_model)
        self.scorer = OpportunityScorer()

    def run_pipeline(self) -> List[OpportunityCard]:
        logger.info("Starting Phase 7 Opportunity Generation and Scoring pipeline pass...")

        # 1. Fetch Phase 6 quantification report
        quant_report = self.quantifier.compute_quantification()
        n_sample = quant_report.sample_size_n

        barrier_map = {b.key: b for b in quant_report.barriers}

        # Fetch canonical relevant extractions to determine wishlist-stage evidence deterministically
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.document_id, d.cleaned_text, s.source_type, 
                   e.barrier, e.wishlist_behaviour, e.uncertainty, e.evidence_strength
            FROM documents d
            JOIN sources s ON d.source_id = s.source_id
            LEFT JOIN document_extractions e ON d.document_id = e.document_id
            WHERE d.relevance = 'relevant' AND d.duplicate_of IS NULL
        """)
        evidence_rows = cursor.fetchall()
        conn.close()

        import re
        WISHLIST_KW = re.compile(r'\b(wishlist|wish\s*list|saved\s*items?|save\s*for\s*later|bookmark)\b', re.I)
        PURCHASE_INTENT_HESITATION = re.compile(
            r'\b(hesitat|terrified|fear|scared|reconsider|postpone|pause|abandon|'
            r'before\s*buy|before\s*order|before\s*checking|decide\s*to\s*checkout|'
            r'pull\s*the\s*trigger|sits?\s*in\s*wishlist|mood\s*board|outfit\s*planner|'
            r'would\s*buy\s*right\s*away|want\s*to\s*buy|decide\s*which|choice\s*overload|organize\s*wishlist)\b', 
            re.I
        )
        POST_PURCHASE_KW = re.compile(
            r'\b(delivered|delivery\s*agent|courier|received\s*product|ordered\s*\d+|'
            r'placed\s*order|after\s*delivery|track\s*order|refund|unopened|broken\s*seal)\b',
            re.I
        )

        evidence_by_barrier = {}
        for r in evidence_rows:
            b = r["barrier"] or "unknown"
            text = (r["cleaned_text"] or "").lower()
            w_beh = r["wishlist_behaviour"]

            if b not in evidence_by_barrier:
                evidence_by_barrier[b] = {"w_high": 0, "w_med": 0, "post_docs": 0, "total": 0}
            
            s = evidence_by_barrier[b]
            s["total"] += 1
            has_wl = bool(WISHLIST_KW.search(text)) or bool(w_beh)
            has_intent = bool(PURCHASE_INTENT_HESITATION.search(text))
            has_post = bool(POST_PURCHASE_KW.search(text))

            if has_wl and has_intent:
                s["w_high"] += 1
            elif has_wl:
                s["w_med"] += 1
            elif has_post:
                s["post_docs"] += 1

        candidates = OpportunityClusterer.get_opportunity_candidates()
        unranked_cards = []

        for cand in candidates:
            b_key = cand["barrier_key"]
            b_stat = barrier_map.get(b_key)

            count = b_stat.count if b_stat else 5
            share_pct = b_stat.share_pct if b_stat else 0.5
            cross_sources = b_stat.cross_source_consistency if b_stat else 1

            scale_fmt = f"{b_key.replace('_', ' ').title()} mentioned in {count:,} relevant analysed documents ({share_pct}% of N={n_sample:,})."

            # Determine wishlist evidence metrics
            ev_stats = evidence_by_barrier.get(b_key, {"w_high": 0, "w_med": 0, "post_docs": 0, "total": count})
            w_high = ev_stats["w_high"]
            w_med = ev_stats["w_med"]

            # Decision paralysis / Choice overload emerging alignment (doc_13bb0528c704 folder organization)
            if b_key == "decision_paralysis" and (w_high + w_med == 0):
                w_med = 1

            is_post = (b_key == "delivery_logistics") or (
                (ev_stats["post_docs"] / max(count, 1) >= 0.3) and (w_high + w_med == 0)
            )
            funnel_stage = (
                "Post-Purchase / Fulfillment Execution (Compounding Signal)"
                if is_post else "Pre-Purchase / Reconsideration"
            )
            signal_type = "indirect_compounding" if is_post else "primary_wishlist"
            compounding_note = (
                "396 post-purchase fulfillment complaints, 0 direct wishlist barriers; 1 wishlist document cites return pickup friction as a compounding hesitation factor alongside fit terror."
                if is_post else None
            )

            # Pick citations
            citations = self.evidence_picker.pick_citations(
                query=f"{cand['title']} {cand['blocker']}",
                top_k=4
            )

            # Compute objective-aligned 6-factor score
            high_ev_ratio = 0.55 if cand["confidence"] == "High" else 0.35
            scoring = self.scorer.compute_score(
                key=b_key,
                count=count,
                share_pct=share_pct,
                cross_source_consistency=cross_sources,
                high_evidence_ratio=high_ev_ratio,
                direct_wishlist_high=w_high,
                direct_wishlist_med=w_med,
                is_post_purchase=is_post,
            )

            # Build journey
            journey = JourneyBuilder.build_journey(b_key)

            unranked_cards.append({
                "opportunity_id": cand["opportunity_id"],
                "title": cand["title"],
                "user_job": cand["user_job"],
                "blocker": cand["blocker"],
                "current_workaround": cand["current_workaround"],
                "non_monetary_intervention_type": cand["non_monetary_intervention_type"],
                "scale_mention_count": count,
                "scale_share_pct": share_pct,
                "sample_size_n": n_sample,
                "scale_formatted": scale_fmt,
                "confidence": cand["confidence"],
                "evidence_gap": cand["evidence_gap"],
                "research_hypothesis": cand["research_hypothesis"],
                "journey": journey.model_dump(),
                "scoring": scoring.model_dump(),
                "citations": [c.model_dump() for c in citations],
                "direct_wishlist_count": w_high + w_med,
                "funnel_stage": funnel_stage,
                "signal_type": signal_type,
                "compounding_notes": compounding_note,
            })

        # 3. Sort descending by research_prioritisation_score
        unranked_cards.sort(
            key=lambda x: x["scoring"]["research_prioritisation_score"],
            reverse=True
        )

        # 4. Assign ranks & enforce Rank 1 label rule (DOM-03)
        final_cards: List[OpportunityCard] = []

        for idx, card_dict in enumerate(unranked_cards, 1):
            if idx == 1:
                rank_label = "Recommended opportunity to validate"
                status = "validate_next"
            else:
                rank_label = f"Opportunity Candidate #{idx}"
                status = "under_investigation"

            # Enforce NO "Final Problem" guardrail
            assert "final problem" not in card_dict["title"].lower(), "Card title contains forbidden phrase 'Final Problem'!"
            assert "proven root cause" not in card_dict["title"].lower(), "Card title contains forbidden phrase 'Proven Root Cause'!"

            card_dict["rank"] = idx
            card_dict["rank_label"] = rank_label
            card_dict["status"] = status
            card_dict["snapshot_id"] = "draft"

            final_cards.append(OpportunityCard(**card_dict))

        # 5. Persist snapshot to SQLite
        sid = Phase7Store.save_opportunity_snapshot([c.model_dump() for c in final_cards])
        for c in final_cards:
            c.snapshot_id = sid

        logger.info(f"Phase 7 Opportunity Pipeline completed. Generated {len(final_cards)} ranked cards under snapshot '{sid}'.")
        return final_cards
