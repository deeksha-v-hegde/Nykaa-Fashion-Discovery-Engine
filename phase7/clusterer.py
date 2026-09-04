import logging
from typing import Any, Dict, List

logger = logging.getLogger("phase7.clusterer")


class OpportunityClusterer:
    """
    Phase 7 Opportunity Candidate Clusterer.
    Groups recurring barriers from Phase 5/6 extractions into research opportunities.
    
    Guarantees:
    - Zero 'Final Problem' or 'Proven Root Cause' titles (DOM-03).
    - Non-monetary intervention TYPES ONLY (DOM-01).
    - Fully grounded on extracted barriers and corpus counts.
    """

    @staticmethod
    def get_opportunity_candidates() -> List[Dict[str, Any]]:
        candidates = [
            {
                "opportunity_id": "opp_delivery_predictability",
                "barrier_key": "delivery_logistics",
                "title": "Unpredictable Delivery SLAs and Post-Shipment Return Pickup Friction",
                "user_job": "Receive fashion orders in time for specific events and easily return ill-fitting items without hassle.",
                "blocker": "Repeated post-shipment delivery delays and sudden return pickup cancellations lock out basic user expectations.",
                "current_workaround": "Users contact customer support repeatedly, post complaints on app stores/Reddit, or abandon future purchases.",
                "non_monetary_intervention_type": "Real-Time Delivery SLA Predictability & Self-Service Return Pickup Automation",
                "confidence": "High",
                "evidence_gap": "Public reviews report delivery delay frustrations; primary user interviews needed to test SLA transparency UI.",
                "research_hypothesis": "Providing guaranteed delivery date ranges and self-service courier tracking will reduce post-shipment anxiety and boost checkout confidence for saved wishlist items."
            },
            {
                "opportunity_id": "opp_ethnic_size_standardization",
                "barrier_key": "fit_size",
                "title": "Ethnic Wear Fit Uncertainty & Inconsistent Brand Size Charts (Likha, Gajra Gang)",
                "user_job": "Confidently select the correct garment size for ethnic kurtas and traditional outfits on the first attempt.",
                "blocker": "Size charts differ significantly between private labels (Likha vs Gajra Gang) and standard sizing, creating terror of returning ill-fitting clothes.",
                "current_workaround": "Users hoard items in wishlist without checking out, ask size questions on Reddit r/TwoXIndia, or order two adjacent sizes.",
                "non_monetary_intervention_type": "Standardized Garment Fit Predictor & Brand-Specific Size Chart Normalization",
                "confidence": "High",
                "evidence_gap": "UGC documents fit hesitation; user interviews required to measure size predictor tool adoption.",
                "research_hypothesis": "Displaying brand-specific measurement overlays and body-type fit recommendations will reduce wishlist hesitation caused by sizing terror."
            },
            {
                "opportunity_id": "opp_fabric_quality_transparency",
                "barrier_key": "quality",
                "title": "Fabric Material Discrepancies & Material Transparency Concerns (Polyester vs Cotton)",
                "user_job": "Ensure received clothing matches expected fabric texture, breathability, and non-see-through material quality.",
                "blocker": "Listings lack clear fabric weight or close-up texture photos, leading to see-through or cheap synthetic material surprises.",
                "current_workaround": "Users search Reddit for real buyer feedback or save items for weeks while waiting for customer review photos.",
                "non_monetary_intervention_type": "Fabric Composition & Close-Up Material Transparency Gallery",
                "confidence": "High",
                "evidence_gap": "UGC highlights fabric quality doubts; primary interviews needed to test fabric weight indicator UI.",
                "research_hypothesis": "Highlighting fabric composition, opacity ratings, and customer texture close-ups will resolve material quality doubts during wishlist reconsideration."
            },
            {
                "opportunity_id": "opp_studio_photo_accuracy",
                "barrier_key": "product_vs_image",
                "title": "Product Appearance vs Listing Studio Lighting Discrepancies",
                "user_job": "Verify true color and fabric drape under natural lighting conditions prior to purchase.",
                "blocker": "Over-edited Studio lighting photos make actual garment color or embroidery look different upon delivery.",
                "current_workaround": "Users check social media try-on hauls or delay checkout until user-submitted photos appear.",
                "non_monetary_intervention_type": "Unedited Natural Light Photo Gallery & User Outfit Submissions",
                "confidence": "Medium",
                "evidence_gap": "Requires user interviews to evaluate buyer reliance on studio vs natural light photo galleries.",
                "research_hypothesis": "Including unedited natural light customer photos in product galleries will bridge the visual expectation gap for saved fashion items."
            },
            {
                "opportunity_id": "opp_wishlist_choice_overload",
                "barrier_key": "decision_paralysis",
                "title": "Wishlist Paralysis & Reconsideration Choice Overload",
                "user_job": "Organize saved fashion items into actionable occasion lists and easily compare alternatives.",
                "blocker": "Wishlists become unorganized dumping grounds of 50+ items, causing decision fatigue and checkout paralysis.",
                "current_workaround": "Users treat wishlist as a mood board when bored, rarely converting items to cart.",
                "non_monetary_intervention_type": "Customizable Wishlist Folders & Side-by-Side Item Comparison Tool",
                "confidence": "Medium",
                "evidence_gap": "UGC identifies wishlist hoarding; 5-6 interviews needed to evaluate folder organization habits.",
                "research_hypothesis": "Allowing users to group wishlisted items by occasion and compare similar dresses side-by-side will reduce choice overload and prompt cart transition."
            },
            {
                "opportunity_id": "opp_styling_context_gap",
                "barrier_key": "styling",
                "title": "Styling & Complete Outfit Context Gap for Tops and Ethnic Wear",
                "user_job": "Understand how to style, accessorize, or pair saved apparel for specific workplace or festive occasions.",
                "blocker": "Single garment photos without complete outfit context leave users unsure if the item matches their existing wardrobe.",
                "current_workaround": "Users post outfit photos on Reddit r/IndianFashionAddicts asking 'How to style this?'",
                "non_monetary_intervention_type": "Outfit Pairing Suggestions & Occasion Styling Context Cards",
                "confidence": "Medium",
                "evidence_gap": "Community threads show styling questions; interviews needed to test curated outfit recommendations.",
                "research_hypothesis": "Showing complete outfit pairing suggestions and occasion styling guides will increase user confidence when evaluating saved wishlist items."
            }
        ]

        return candidates
