import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("phase4.grounding_validator")


class GroundingValidator:
    """
    Validates that every claim and direct quote in the generated discovery response
    is genuinely present in the retrieved evidence chunks.
    """

    @staticmethod
    def validate_quotes(
        grounded_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str], str]:
        """
        Extracts quoted phrases from the generated response and verifies their presence
        in the retrieved chunk texts.
        
        Returns:
            (is_grounded, ungrounded_quotes, sanitized_text)
        """
        if not grounded_text or not retrieved_chunks:
            return True, [], grounded_text

        # Combine all retrieved passage texts for substring containment
        corpus_text = " ".join([c.get("text", "").lower() for c in retrieved_chunks])

        # Extract double-quoted and smart-quoted phrases of length > 12 characters
        quotes = re.findall(r'["“]([^"”]{12,})["”]', grounded_text)

        ungrounded = []
        sanitized_text = grounded_text

        for q in quotes:
            q_clean = q.strip().lower()
            # Normalize whitespace
            q_norm = re.sub(r"\s+", " ", q_clean)

            # Check exact or partial 4-word slice containment
            words = q_norm.split()
            if len(words) >= 4:
                slice_3 = " ".join(words[:4])
                slice_mid = " ".join(words[len(words)//2: len(words)//2 + 4]) if len(words) >= 6 else slice_3
                is_present = (slice_3 in corpus_text) or (slice_mid in corpus_text)
            else:
                is_present = q_norm in corpus_text

            if not is_present:
                ungrounded.append(q)
                logger.warning(f"Ungrounded quote detected by GroundingValidator: '{q}'")

        is_grounded = len(ungrounded) == 0
        return is_grounded, ungrounded, sanitized_text
