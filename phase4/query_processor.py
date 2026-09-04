import re
from typing import Optional


class QueryProcessor:
    """
    Sanitizes and normalizes user discovery queries for optimal hybrid retrieval.
    Strictly forbidden from adding facts, assumptions, or external context.
    """

    @staticmethod
    def process_query(query: str) -> str:
        if not query:
            return ""

        # Normalize multiple whitespaces
        cleaned = re.sub(r"\s+", " ", query).strip()

        # Strip trailing conversational punctuation while preserving hyphens and contractions
        cleaned = re.sub(r"[?!.,;:]+$", "", cleaned).strip()

        return cleaned
