from typing import Any, Dict
from config.settings import Settings
from phase7.models import ScoringBreakdown


class OpportunityScorer:
    """
    Phase 7 Opportunity Scorer.
    Calculates transparent 6-factor scores (1.0-5.0 scale) and weighted research prioritisation score.
    """

    def __init__(self):
        settings = Settings()
        self.weights = {
            "weight_frequency": settings.weight_frequency,
            "weight_metric_relevance": settings.weight_metric_relevance,
            "weight_pain": settings.weight_pain,
            "weight_evidence": settings.weight_evidence,
            "weight_cross_source": settings.weight_cross_source,
            "weight_solvability": settings.weight_solvability,
        }

    def compute_score(
        self,
        key: str,
        count: int,
        share_pct: float,
        cross_source_consistency: int,
        high_evidence_ratio: float = 0.5,
        direct_wishlist_high: int = 0,
        direct_wishlist_med: int = 0,
        is_post_purchase: bool = False,
    ) -> ScoringBreakdown:
        """
        Computes 6 individual factor scores and weighted research prioritisation score.
        Objective-aligned: Evaluates wishlist-stage purchase hesitation relevance from evidence.
        """

        # 1. Frequency Score (1-5)
        # Evaluates frequency of friction across canonical relevant sample (N=1,025).
        # For post-purchase complaints without direct wishlist evidence, raw frequency reflects
        # delivery execution tickets, not wishlist hesitation; effective frequency is capped at 4.0 as a compounding signal.
        if is_post_purchase:
            score_freq = 4.0
        else:
            if share_pct >= 8.0:
                score_freq = 4.5
            elif share_pct >= 4.0:
                score_freq = 4.0
            elif share_pct >= 2.0:
                score_freq = 3.5
            elif share_pct >= 0.5:
                score_freq = 3.0
            else:
                score_freq = 2.5

        # 2. Metric Relevance Score (1-5) — Proximity to 30-Day Wishlist Reconsideration & Purchase
        # Deterministically derived from wishlist-stage evidence signals:
        # - Post-purchase delivery execution without direct wishlist evidence: 2.3 (indirect compounding signal)
        # - Pre-purchase barriers with direct wishlist evidence: 4.0 base + 0.2*min(high,4) + 0.1*min(med,2)
        # - Pre-purchase barriers without explicit wishlist keywords: 3.5 baseline
        total_wl = direct_wishlist_high + direct_wishlist_med
        if is_post_purchase:
            score_metric = 2.3
        elif total_wl > 0:
            score_metric = min(5.0, 4.0 + 0.2 * min(direct_wishlist_high, 4) + 0.1 * min(direct_wishlist_med, 2))
        else:
            score_metric = 3.5

        # 3. User Pain Severity Score (1-5)
        pain_map = {
            "fit_size": 4.7,
            "quality": 4.6,
            "delivery_logistics": 4.5,
            "product_vs_image": 4.2,
            "decision_paralysis": 3.9,
            "styling": 3.8,
            "price_timing": 3.5,
            "social_validation": 3.2,
            "availability": 3.0,
            "other_emerging": 3.5
        }
        score_pain = pain_map.get(key, 3.5)

        # 4. Evidence Strength Score (1-5)
        if high_evidence_ratio >= 0.45:
            score_evidence = 4.6
        elif high_evidence_ratio >= 0.25:
            score_evidence = 4.0
        else:
            score_evidence = 3.2

        # 5. Cross-Source Consistency Score (1-5)
        score_cross = 5.0 if cross_source_consistency >= 2 else 2.5

        # 6. Non-Monetary Product Solvability Score (1-5)
        solvability_map = {
            "fit_size": 4.8,
            "quality": 4.6,
            "styling": 4.4,
            "delivery_logistics": 4.4,
            "product_vs_image": 4.3,
            "decision_paralysis": 4.2,
            "price_timing": 3.5,
            "social_validation": 3.5,
            "availability": 3.0,
            "other_emerging": 3.8
        }
        score_solvability = solvability_map.get(key, 3.8)

        # Weighted Sum
        weighted_score = (
            score_freq * self.weights["weight_frequency"] +
            score_metric * self.weights["weight_metric_relevance"] +
            score_pain * self.weights["weight_pain"] +
            score_evidence * self.weights["weight_evidence"] +
            score_cross * self.weights["weight_cross_source"] +
            score_solvability * self.weights["weight_solvability"]
        )

        return ScoringBreakdown(
            score_frequency=round(score_freq, 2),
            score_metric_relevance=round(score_metric, 2),
            score_pain=round(score_pain, 2),
            score_evidence=round(score_evidence, 2),
            score_cross_source=round(score_cross, 2),
            score_solvability=round(score_solvability, 2),
            research_prioritisation_score=round(weighted_score, 2),
            weights_used=self.weights
        )
