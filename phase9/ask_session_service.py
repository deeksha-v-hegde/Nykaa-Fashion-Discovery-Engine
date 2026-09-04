import logging
import uuid
from typing import Any, Dict, List, Optional

from phase4.ask_engine import AskEngine
from phase4.models import DiscoveryResponse
from phase7.store import Phase7Store
from phase9.models import (
    AskSessionState,
    FollowUpChipItem,
    GroundedAskSectionPayload,
)
from phase9.presets_catalogue import PresetsCatalogue

logger = logging.getLogger("phase9.ask_session_service")


class AskSessionService:
    """
    Phase 9 Session & Structured RAG Service.
    Orchestrates Phase 4 AskEngine RAG pipeline and formats responses into
    9 distinct, transparent UI sections.
    """

    def __init__(self):
        self.ask_engine = AskEngine()
        self.sessions: Dict[str, AskSessionState] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> AskSessionState:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        sid = session_id or f"ask_sess_{uuid.uuid4().hex[:12]}"
        state = AskSessionState(session_id=sid)
        self.sessions[sid] = state
        return state

    def execute_ask_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a primary or follow-up Ask query and returns 9 structured sections.
        """
        session = self.get_or_create_session(session_id)
        filters_dict = filters or {}

        res: DiscoveryResponse = self.ask_engine.ask(
            query=query,
            filters=filters_dict,
            top_k=session.active_filters.get("top_k", 5)
        )

        # Map related opportunities from Phase 7
        opp_cards = Phase7Store.get_latest_opportunities()
        related_ids = []
        related_titles = []

        q_lower = query.lower()
        for opp in opp_cards:
            b_type = opp.get("blocker", "").lower()
            t_type = opp.get("title", "").lower()
            if any(kw in q_lower for kw in ["fit", "size", "sizing"]) and "fit" in t_type:
                related_ids.append(opp["opportunity_id"])
                related_titles.append(opp["title"])
            elif any(kw in q_lower for kw in ["delivery", "delay", "return"]) and "delivery" in t_type:
                related_ids.append(opp["opportunity_id"])
                related_titles.append(opp["title"])
            elif any(kw in q_lower for kw in ["quality", "fabric", "cotton"]) and "fabric" in t_type:
                related_ids.append(opp["opportunity_id"])
                related_titles.append(opp["title"])

        if not related_ids and opp_cards:
            related_ids.append(opp_cards[0]["opportunity_id"])
            related_titles.append(opp_cards[0]["title"])

        # Format 9 distinct sections
        payload = GroundedAskSectionPayload(
            grounded_answer=res.grounded_answer,
            evidence_passages=res.evidence,
            pattern_summary=f"Retrieved {len(res.evidence)} verbatim chunk citations.",
            inference_narrative=res.inference,
            confidence_rating=res.confidence,
            confidence_rationale=res.confidence_reason,
            evidence_gap=res.evidence_gap or "30-day wishlist completion rate cannot be tracked from public UGC; metric hop strictly unknown.",
            metric_connection=res.metric_connection.explanation if res.metric_connection else "Wishlist item added -> Reconsideration friction -> Purchase confidence unbuilt -> 30-day completion: UNKNOWN.",
            related_opportunity_ids=related_ids,
            related_opportunity_titles=related_titles,
            suggested_followups=PresetsCatalogue.get_followup_chips()
        )

        session.history.append({
            "query": query,
            "outcome": res.status,
            "confidence": res.confidence,
            "citations_count": len(res.evidence)
        })

        return {
            "status": "success",
            "session_id": session.session_id,
            "outcome_status": res.status,
            "sections": payload.model_dump(),
            "nykaa_evidence_limited": res.nykaa_evidence_limited
        }
