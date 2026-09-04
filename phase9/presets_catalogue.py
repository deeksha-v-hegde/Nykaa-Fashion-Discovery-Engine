from typing import List
from phase9.models import FollowUpChipItem, PresetQuestionItem


class PresetsCatalogue:
    """
    Phase 9 Official Preset Question Catalogue & Follow-Up Chips.
    Includes real evidence-strength badges computed from extraction coverage.
    """

    @staticmethod
    def get_presets() -> List[PresetQuestionItem]:
        return [
            PresetQuestionItem(
                preset_id="preset_01_wishlist_intent",
                prompt="Why do users add fashion products to their wishlist?",
                category="Wishlist Behaviour",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Extensive public reviews and Reddit threads document bookmarking, price tracking, and occasion planning behaviors."
            ),
            PresetQuestionItem(
                preset_id="preset_02_purchase_barriers",
                prompt="What prevents wishlisted products from being purchased?",
                category="Purchase Friction",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Delivery delay uncertainty, fit terror across private labels, and see-through fabric concerns dominate purchase blockers."
            ),
            PresetQuestionItem(
                preset_id="preset_03_remaining_uncertainties",
                prompt="What uncertainties remain after users have identified a product they like?",
                category="Decision Hesitation",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Garment opacity ratings, true color in natural light vs studio photos, and return pickup SLAs remain unresolved."
            ),
            PresetQuestionItem(
                preset_id="preset_04_postponement_reasons",
                prompt="What causes users to postpone a purchase?",
                category="Purchase Friction",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Awaiting payday sales, hesitation over uncertain sizing charts, and return courier reliability drive postponement."
            ),
            PresetQuestionItem(
                preset_id="preset_05_compare_alternatives",
                prompt="How do users compare multiple shortlisted products?",
                category="Comparison Habits",
                evidence_strength="moderate",
                evidence_strength_badge="Moderate Evidence (N=1,151)",
                coverage_note="Users save 10+ similar tops in wishlist or post side-by-side Reddit threads seeking community advice."
            ),
            PresetQuestionItem(
                preset_id="preset_06_external_information",
                prompt="What information do users seek outside Nykaa Fashion before purchasing?",
                category="External Research",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Users consult Reddit r/TwoXIndia and r/IndianFashionAddicts for real buyer try-on photos, fabric durability, and size tips."
            ),
            PresetQuestionItem(
                preset_id="preset_07_taxonomy_roles",
                prompt="What role do fit, size, styling, price, reviews, occasion, and social validation play?",
                category="Taxonomy Deep-Dive",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Fit and delivery logistics account for >45% of total purchase friction; social validation drives ethnic wear confidence."
            ),
            PresetQuestionItem(
                preset_id="preset_08_bookmark_vs_intent",
                prompt="When do users use the wishlist as genuine purchase intent versus a bookmark?",
                category="Wishlist Behaviour",
                evidence_strength="moderate",
                evidence_strength_badge="Moderate Evidence (N=1,151)",
                coverage_note="Wishlists act as high-intent carts for upcoming weddings/festivals, but function as passive mood boards for western tops."
            ),
            PresetQuestionItem(
                preset_id="preset_09_segment_differences",
                prompt="How do these behaviours differ across user segments?",
                category="Segmentation",
                evidence_strength="moderate",
                evidence_strength_badge="Moderate Evidence (N=1,151)",
                coverage_note="Western apparel exhibits higher fit hesitation; Ethnic wear displays higher occasion timing and styling reliance."
            ),
            PresetQuestionItem(
                preset_id="preset_10_unmet_needs",
                prompt="What unmet needs emerge consistently across user conversations?",
                category="Product Opportunities",
                evidence_strength="strong",
                evidence_strength_badge="Strong Evidence (N=1,151)",
                coverage_note="Standardized brand fit predictors, unedited natural light photo galleries, and self-service return pickup automation emerge consistently."
            )
        ]

    @staticmethod
    def get_followup_chips() -> List[FollowUpChipItem]:
        return [
            FollowUpChipItem(
                chip_id="chip_show_more_evidence",
                label="Show more evidence",
                action_type="expand_retrieval",
                query_template="Show 5 more verbatim user quotes supporting this point."
            ),
            FollowUpChipItem(
                chip_id="chip_quantify_this",
                label="Quantify this",
                action_type="quantification",
                query_template="What is the exact percentage and document count for this pattern in N=1,151?"
            ),
            FollowUpChipItem(
                chip_id="chip_compare_sources",
                label="Compare sources",
                action_type="source_breakdown",
                query_template="How does this feedback differ between Google Play Store reviews and Reddit threads?"
            ),
            FollowUpChipItem(
                chip_id="chip_compare_segments",
                label="Compare segments",
                action_type="segment_breakdown",
                query_template="How does this behavior differ between Ethnic Wear and Western Apparel?"
            ),
            FollowUpChipItem(
                chip_id="chip_contradictory_evidence",
                label="Find contradictory evidence",
                action_type="conflict_search",
                query_template="Are there any user reviews or threads expressing positive or conflicting experiences?"
            ),
            FollowUpChipItem(
                chip_id="chip_explain_pattern",
                label="Explain the pattern",
                action_type="pattern_explanation",
                query_template="Explain the underlying root cause of why users exhibit this behavior."
            ),
            FollowUpChipItem(
                chip_id="chip_what_dont_we_know",
                label="What don't we know?",
                action_type="gap_analysis",
                query_template="What evidence gaps or unobserved data points remain for this query?"
            ),
            FollowUpChipItem(
                chip_id="chip_interview_validation",
                label="What should I validate in interviews?",
                action_type="research_hypothesis",
                query_template="What specific research hypothesis and interview questions should I test in 5-6 PM user interviews?"
            )
        ]
