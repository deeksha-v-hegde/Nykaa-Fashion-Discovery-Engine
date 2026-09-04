import re
from typing import Optional


class QueryProcessor:
    """
    Sanitizes, normalizes, and expands user discovery queries for optimal hybrid retrieval.
    Expands abstract PM terminology into fashion e-commerce behavioral signals present in consumer reviews.
    """

    EXPANSION_PATTERNS = [
        (r"\buser segments\b|\bsegments\b|\bdiffer across\b", "exploratory browsing high purchase intent bookmarking occasion shopping evaluation"),
        (r"\bunmet needs\b|\bemerge consistently\b", "friction sizing charts fabric quality return pickup packaging customer support wishlist folders"),
        (r"\bgenuine purchase intent\b|\bintent versus a bookmark\b|\bbookmark vs intent\b", "purchase intent bookmarking save for later occasion need payday hesitation"),
        (r"\bcompare multiple\b|\bshortlisted products\b|\bcompare alternatives\b", "compare alternatives sizing fabric reviews photos shortlist decision"),
        (r"\bseek outside\b|\bexternal information\b|\boutside nykaa\b", "reddit reviews try-on photos sizing validation external opinions"),
        (r"\bpostpone\b|\bdelay\b", "hesitation sizing doubt price consideration return reliability postponement"),
    ]

    @staticmethod
    def process_query(query: str) -> str:
        if not query:
            return ""

        # Normalize multiple whitespaces
        cleaned = re.sub(r"\s+", " ", query).strip()

        # Strip trailing conversational punctuation while preserving hyphens and contractions
        cleaned = re.sub(r"[?!.,;:]+$", "", cleaned).strip()

        # Enhance query with semantic domain keywords if abstract PM phrase detected
        q_lower = cleaned.lower()
        expanded_terms = []
        for pattern, terms in QueryProcessor.EXPANSION_PATTERNS:
            if re.search(pattern, q_lower):
                expanded_terms.append(terms)

        if expanded_terms:
            return f"{cleaned} {' '.join(expanded_terms)}"

        return cleaned
