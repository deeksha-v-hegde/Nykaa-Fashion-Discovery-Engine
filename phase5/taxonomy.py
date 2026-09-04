"""
Phase 5 Taxonomy Definitions and Enum Allow-Lists.
Defines Wishlist Behaviours, Purchase Barriers, and Evidence Strength ratings.
"""

from typing import List, Set

# Wishlist Behaviour Taxonomy
WISHLIST_BEHAVIOURS: List[str] = [
    "genuine_purchase_intent",
    "bookmark_save_for_later",
    "compare_alternatives",
    "future_occasion",
    "waiting_timing",
    "need_more_information",
    "inspiration",
    "price_monitoring",
    "other"
]

# Purchase Barrier Taxonomy
PURCHASE_BARRIERS: List[str] = [
    "fit_size",
    "quality",
    "product_vs_image",
    "styling",
    "decision_paralysis",
    "price_timing",
    "availability",
    "social_validation",
    "reviews_information",
    "occasion_timing",
    "trust",
    "delivery_logistics",
    "other_emerging"
]

# Evidence Strength Ratings
EVIDENCE_STRENGTHS: Set[str] = {"high", "medium", "low"}

# Description map for grounding
BARRIER_DESCRIPTIONS = {
    "fit_size": "Inconsistent sizing charts, wrong fit, fear of returning due to size mismatch.",
    "quality": "Poor fabric material, see-through cloth, cheap stitching, quick wear-and-tear.",
    "product_vs_image": "Color or appearance differs from website photos, misleading lighting.",
    "styling": "Unsure how to style or pair the item, lack of model outfit context.",
    "decision_paralysis": "Too many choices, wishlist hoarding, indecision over colors/patterns.",
    "price_timing": "Waiting for salary payday, festive sale, or budget constraints.",
    "availability": "Desired size or color out of stock after saving.",
    "social_validation": "Seeking opinions from friends, Reddit, or social media before buying.",
    "reviews_information": "Lack of customer reviews, photos, or detailed fabric composition details.",
    "occasion_timing": "Saving for a wedding, trip, or event that is weeks away.",
    "trust": "Skepticism about brand authenticity, seller credibility, or customer support.",
    "delivery_logistics": "Delayed delivery times, unpredictable return pickup experience.",
    "other_emerging": "Novel or unclassified friction point."
}
