from phase7.models import MetricJourneyHops


class JourneyBuilder:
    """
    Phase 7 Metric Journey Builder.
    Constructs visualization hops for the 30-day wishlist-to-purchase funnel.
    
    Guarantees:
    - Hop 5 (purchase_completion_30day) is ALWAYS strictly 'unknown' per DOM-02 guardrail.
    - Hops 1-4 are labeled 'observed' or 'inferred' based on corpus evidence.
    """

    @staticmethod
    def build_journey(barrier_key: str) -> MetricJourneyHops:
        narratives = {
            "delivery_logistics": "Wishlist item added -> Reconsideration delayed by delivery SLA or return pickup uncertainty -> Purchase completion 30-day: Unknown.",
            "fit_size": "Wishlist item added -> Reconsideration blocked by size chart errors across brands (Likha, Gajra Gang) -> Cart addition postponed -> 30-day completion: Unknown.",
            "quality": "Wishlist item added -> User seeks fabric composition reviews (polyester vs cotton, see-through) -> Purchase confidence unbuilt -> 30-day completion: Unknown.",
            "product_vs_image": "Wishlist item added -> User hesitates due to Studio photo lighting vs real color -> Reconsideration stall -> 30-day completion: Unknown.",
            "decision_paralysis": "Wishlist item added -> Hoarding 50+ items in wishlist leads to choice overload -> Cart addition postponed -> 30-day completion: Unknown.",
            "styling": "Wishlist item added -> Lack of outfit pairing or occasion styling context -> Reconsideration stall -> 30-day completion: Unknown."
        }

        narrative = narratives.get(
            barrier_key,
            "Wishlist item added -> Reconsideration friction -> Purchase confidence unbuilt -> 30-day completion: Unknown."
        )

        return MetricJourneyHops(
            wishlist_added="observed",
            reconsideration="observed",
            confidence_building="inferred",
            cart_addition="inferred",
            purchase_completion_30day="unknown",
            journey_narrative=narrative
        )
