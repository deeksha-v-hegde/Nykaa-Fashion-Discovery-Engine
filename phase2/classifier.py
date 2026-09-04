import re
from typing import Dict, List, Optional, Tuple


class RelevanceClassifier:
    """
    Phase 2 Relevance Classifier.
    Evaluates whether an ingested document is relevant to the Nykaa Fashion wishlist-to-purchase
    discovery problem (30-day conversion barriers).

    Grounding Criteria:
    - Relevant:
        * Wishlist/Cart hesitation, saving items, price drop tracking, 30-day conversion delays
        * Sizing and fit uncertainty, body type matching, Indian ethnic sizing variances
        * Fabric feel, material quality, see-through cloth, photo vs reality mismatch
        * Need for user styling advice, real customer photos, social validation for outfits
        * Return, replacement, and pickup cancellation friction impacting shopping confidence
        * Brand trust, curated fashion discovery vs generic marketplaces
    - Not Relevant:
        * General non-fashion life advice, dating, careers, politics
        * Generic app crashes or OTP bugs with zero shopping/cart context
        * Low-information 1-3 word reviews ("good app", "nice", "ok", "super", "worst")
    """

    # Primary fashion product / shopping anchors
    FASHION_ANCHORS = re.compile(
        r"\b(fashion|clothes|clothing|outfit|dress|dresses|kurta|kurti|saree|sari|lehenga|dupatta|"
        r"jeans|top|tops|skirt|blouse|lingerie|bra|heels|shoes|footwear|jewellery|jewelry|handbag|"
        r"apparel|wear|ethnic|western|fabric|cloth|kapda|material|size|sizing|fit|fitting|wishlist|"
        r"cart|order|orders|shopping|store|myntra|nykaa|ajio|zara|h&m|urbanic|westside|meesho|snitch)\b",
        re.IGNORECASE
    )

    # Domain-specific positive relevance keyword and regex patterns
    POSITIVE_FACET_PATTERNS = {
        "wishlist_hesitation": [
            re.compile(r"\b(wishlist|wishlisted|wishlisting|save\s+for\s+later|saved\s+items)\b", re.IGNORECASE),
            re.compile(r"\b(hesitat\w+|delay\w+|postpon\w+|wait\w+\s+for\s+sale|price\s+drop|cart\s+abandon\w+)\b", re.IGNORECASE),
            re.compile(r"\b(in\s+my\s+cart|added\s+to\s+cart|buy\s+later|sitting\s+in\s+cart|second\s+thought)\b", re.IGNORECASE),
            re.compile(r"\b(30\s+days?|months?\s+later|buying\s+decision|purchase\s+intent)\b", re.IGNORECASE)
        ],
        "sizing_and_fit": [
            re.compile(r"\b(siz\w+|fitting|too\s+tight|too\s+loose|size\s+chart|measurements?)\b", re.IGNORECASE),
            re.compile(r"\b(bust|waist|hip|length|petite|plus\s+size|curvy|body\s+type)\b", re.IGNORECASE),
            re.compile(r"\b(xs|small|medium|large|xl|xxl|32[a-d]|34[a-d]|36[a-d]|uk\s*\d+)\b", re.IGNORECASE),
            re.compile(r"\b(inconsisten\w+\s+sizing|runs\s+small|runs\s+large|true\s+to\s+size)\b", re.IGNORECASE)
        ],
        "fabric_and_quality": [
            re.compile(r"\b(fabric|material|cloth|kapda|quality|see[\s-]through|transparent)\b", re.IGNORECASE),
            re.compile(r"\b(polyester|cotton|linen|silk|georgette|rayon|chiffon|denim)\b", re.IGNORECASE),
            re.compile(r"\b(stitch\w+|stitching|color\s+bleed\w*|faded|cheap\s+quality|duplicate)\b", re.IGNORECASE),
            re.compile(r"\b(pictures?\s+vs\s+reality|different\s+from\s+pic\w*|as\s+shown)\b", re.IGNORECASE)
        ],
        "social_validation_and_styling": [
            re.compile(r"\b(review\w*|photo\w*|picture\w*|customer\s+image\w*|real\s+image\w*)\b", re.IGNORECASE),
            re.compile(r"\b(styling|style|pair\w*|how\s+to\s+wear|outfit|recommend\w*)\b", re.IGNORECASE),
            re.compile(r"\b(occasion|wedding|festive|office|party|college|ethnic\s+wear)\b", re.IGNORECASE),
            re.compile(r"\b(kurta|kurti|saree|lehenga|dupatta|jeans|dress|top|footwear|heels)\b", re.IGNORECASE)
        ],
        "returns_and_confidence": [
            re.compile(r"\b(return\w*|exchange\w*|replacement|refund\w*|reverse\s+pickup)\b", re.IGNORECASE),
            re.compile(r"\b(pickup\s+cancel\w*|return\s+policy|store\s+credit|delivery\s+delay)\b", re.IGNORECASE),
            re.compile(r"\b(scared\s+to\s+buy|hesitant\s+to\s+order|risk|waste\s+of\s+money)\b", re.IGNORECASE)
        ],
        "brand_and_comparison": [
            re.compile(r"\b(nykaa\s+fashion|nykaa|myntra|ajio|zara|h&m|urbanic|westside|meesho|tata\s+cliq)\b", re.IGNORECASE),
            re.compile(r"\b(brand\s+reputation|overpriced|worth\s+the\s+price|price\s+vs\s+quality)\b", re.IGNORECASE)
        ]
    }

    # Noise and non-relevant patterns
    GENERIC_NOISE_PATTERNS = [
        re.compile(r"^(good|nice|ok|bad|super|worst|poor|fine|great|awesome|best|useless|helpful|thank\s+you|pls\s+update)(\s+app|\s+service)?\s*[.!]*$", re.IGNORECASE),
        re.compile(r"^(otp\s+not\s+(coming|received)|login\s+problem|unable\s+to\s+login|login\s+issue)\s*[.!]*$", re.IGNORECASE),
        re.compile(r"^\d+$")
    ]

    # Non-fashion off-topic indicators (e.g. general relationship/career posts that mention 'saving' or 'style')
    OFF_TOPIC_PATTERNS = [
        re.compile(r"\b(relationship|boyfriend|girlfriend|dating|cheating|marriage\s+proposal|in-laws|career\s+advice|toxic\s+boss|interview|salary|resignation)\b", re.IGNORECASE)
    ]

    @classmethod
    def classify(cls, text: str, source_scope: str = "nykaa") -> Tuple[str, str, List[str]]:
        """
        Classifies the cleaned document text.
        Returns:
            (relevance: str, relevance_reason: str, matched_facets: List[str])
        """
        if not text or len(text.strip()) < 10:
            return "not_relevant", "Text too short or empty (under 10 characters)", []

        cleaned_lower = text.strip().lower()

        # 1. Check for pure generic noise / 1-word spam
        for pat in cls.GENERIC_NOISE_PATTERNS:
            if pat.match(cleaned_lower):
                return "not_relevant", "Generic one-line noise or technical complaint without shopping context", []

        # 2. Check for explicit off-topic non-fashion themes in broader community discussions
        if source_scope == "broader_fashion":
            has_fashion_anchor = bool(cls.FASHION_ANCHORS.search(text))
            for off_pat in cls.OFF_TOPIC_PATTERNS:
                if off_pat.search(text) and not has_fashion_anchor:
                    return "not_relevant", "Off-topic community discussion (non-fashion personal/relationship context)", []

        # 3. Match domain facets
        matched_facets: List[str] = []
        for facet, patterns in cls.POSITIVE_FACET_PATTERNS.items():
            if any(p.search(text) for p in patterns):
                matched_facets.append(facet)

        # 4. In broader fashion scope, ensure there is at least one fashion anchor
        if source_scope == "broader_fashion":
            if not cls.FASHION_ANCHORS.search(text):
                return "not_relevant", "Community post lacks explicit fashion or shopping terminology", []

        # 5. Decision Logic
        if len(matched_facets) >= 1:
            facets_str = ", ".join(matched_facets)
            return (
                "relevant",
                f"Matches fashion shopping discovery facets: {facets_str}",
                matched_facets
            )

        # For Nykaa app reviews that are moderately long (>80 chars) but don't match specific fashion keywords
        if source_scope == "nykaa" and len(text) >= 80:
            return (
                "unknown",
                "App review with shopping feedback but without explicit fashion discovery keywords",
                []
            )

        return (
            "not_relevant",
            "General text without relevance to fashion wishlist discovery, sizing, fabric, or purchase barriers",
            []
        )
