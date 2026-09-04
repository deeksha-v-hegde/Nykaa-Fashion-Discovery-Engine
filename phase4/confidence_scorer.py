from typing import Any, Dict, List, Literal, Tuple


class ConfidenceScorer:
    """
    Computes grounded confidence rating (High / Medium / Low) based on:
    - Average & maximum retrieval similarity scores
    - Source platform diversity
    - Supporting chunk volume
    - Presence of conflicting viewpoints
    """

    @staticmethod
    def calculate_confidence(
        retrieved_chunks: List[Dict[str, Any]],
        conflict_detected: bool = False
    ) -> Tuple[Literal["High", "Medium", "Low"], str]:
        if not retrieved_chunks:
            return "Low", "No supporting evidence retrieved."

        scores = [c.get("score", 0.0) for c in retrieved_chunks]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        unique_sources = {c.get("source_id") for c in retrieved_chunks if c.get("source_id")}
        unique_platforms = {c.get("platform") for c in retrieved_chunks if c.get("platform")}
        chunk_count = len(retrieved_chunks)

        reasons = []

        # Base confidence from retrieval score & chunk count
        if avg_score >= 0.42 and chunk_count >= 3 and len(unique_platforms) >= 2:
            confidence = "High"
            reasons.append(f"Strong semantic retrieval score (avg: {avg_score:.2f}) across {len(unique_platforms)} platforms ({', '.join(unique_platforms)}).")
        elif avg_score >= 0.32 or chunk_count >= 2:
            confidence = "Medium"
            reasons.append(f"Moderate retrieval score (avg: {avg_score:.2f}) supported by {chunk_count} evidence chunks.")
        else:
            confidence = "Low"
            reasons.append(f"Lower retrieval scores (avg: {avg_score:.2f}) indicating limited semantic overlap in current corpus.")

        if conflict_detected:
            if confidence == "High":
                confidence = "Medium"
            reasons.append("Conflicting user viewpoints detected in corpus; requires user interview validation.")

        if len(unique_sources) == 1:
            reasons.append("Evidence concentrated on a single source register.")

        return confidence, " ".join(reasons)
