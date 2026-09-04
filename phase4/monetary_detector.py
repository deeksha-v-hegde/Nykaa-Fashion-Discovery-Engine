import re
from typing import Tuple

MONETARY_PATTERNS = [
    r"\b(discount|discounts|discounted)\b",
    r"\b(coupon|coupons|promo code|promo codes|promocode|voucher|vouchers)\b",
    r"\b(cashback|cash back|cash-back)\b",
    r"\b(price cut|price drop|price drops|cheaper price|lower price|reduce price)\b",
    r"\b(free shipping coupon|flat 50%|flat 20%|50% off|20% off|offer code)\b",
    r"\b(sale discount|monetary incentive|financial incentive)\b",
    r"\b(credit card discount|bank offer|wallet cashback)\b"
]

REFUSAL_MESSAGE = (
    "Monetary incentives are outside the project scope. "
    "I can instead identify evidence-backed non-monetary barriers and opportunities "
    "that may influence wishlist-to-purchase conversion."
)


class MonetaryDetector:
    """
    Detects monetary and discount-related queries before retrieval.
    Enforces the core non-monetary constraint of the product discovery engine.
    """

    @classmethod
    def check_query(cls, query: str) -> Tuple[bool, str]:
        """
        Returns (is_monetary, refusal_or_reason).
        """
        if not query or not query.strip():
            return False, ""

        q_lower = query.lower()
        for pattern in MONETARY_PATTERNS:
            if re.search(pattern, q_lower):
                return True, REFUSAL_MESSAGE

        return False, ""
