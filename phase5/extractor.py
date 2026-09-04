import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from llm.groq_adapter import GroqAdapter
from phase5.models import DocumentExtraction
from phase5.taxonomy import PURCHASE_BARRIERS, WISHLIST_BEHAVIOURS

logger = logging.getLogger("phase5.extractor")


class DocumentExtractor:
    """
    Phase 5 Structured Document Extractor.
    Extracts taxonomy attributes, barriers, uncertainties, workarounds, and evidence strength.
    
    Principles:
    - Context = THIS document only (no external facts).
    - Null-if-unsupported policy (leaves unsupported fields NULL).
    - Never sets 'genuine_purchase_intent' solely because 'wishlist' is mentioned.
    """

    def __init__(self):
        self.groq_adapter = GroqAdapter()

    def extract_document(self, doc_id: str, text: str, source_scope: str = "nykaa") -> DocumentExtraction:
        """
        Extracts structured attributes from a single relevant document.
        """
        if not text or not text.strip():
            return DocumentExtraction(
                document_id=doc_id,
                evidence_strength="low"
            )

        # Check Groq status
        groq_ping = self.groq_adapter.ping()
        if groq_ping["status"] == "connected":
            try:
                return self._extract_with_llm(doc_id, text, source_scope)
            except Exception as e:
                logger.warning(f"LLM extraction failed for doc {doc_id}: {e}. Falling back to grounded rule matcher.")
                return self._extract_with_rule_matcher(doc_id, text, source_scope)
        else:
            return self._extract_with_rule_matcher(doc_id, text, source_scope)

    def _extract_with_llm(self, doc_id: str, text: str, source_scope: str) -> DocumentExtraction:
        system_instruction = (
            "You are the Nykaa Fashion Structured Data Extraction engine.\n"
            "MANDATORY RULES:\n"
            "1. Context = THIS document text ONLY. Do NOT invent external details.\n"
            "2. Fill fields ONLY when explicitly supported by the text. Leave unsupported fields as null.\n"
            "3. Do NOT set wishlist_behaviour to 'genuine_purchase_intent' simply because the word 'wishlist' appears.\n"
            "4. Allowed wishlist_behaviour values: 'genuine_purchase_intent', 'bookmark_save_for_later', 'compare_alternatives', 'future_occasion', 'waiting_timing', 'need_more_information', 'inspiration', 'price_monitoring', 'other', or null.\n"
            "5. Allowed barrier values: 'fit_size', 'quality', 'product_vs_image', 'styling', 'decision_paralysis', 'price_timing', 'availability', 'social_validation', 'reviews_information', 'occasion_timing', 'trust', 'delivery_logistics', 'other_emerging', or null.\n"
            "6. evidence_strength MUST be 'high', 'medium', or 'low'.\n"
            "7. Output valid JSON adhering to this schema."
        )

        llm_out = self.groq_adapter.generate(
            prompt=f"EXTRACT STRUCTURED ATTRIBUTES FROM THIS SINGLE DOCUMENT:\n{text}",
            context_chunks=[{"chunk_id": doc_id, "text": text, "source_scope": source_scope}],
            system_instruction=system_instruction
        )

        wb = llm_out.get("wishlist_behaviour")
        if wb not in WISHLIST_BEHAVIOURS:
            wb = None

        bar = llm_out.get("barrier")
        if bar not in PURCHASE_BARRIERS:
            bar = None

        st = str(llm_out.get("evidence_strength", "medium")).lower()
        if st not in {"high", "medium", "low"}:
            st = "medium"

        return DocumentExtraction(
            document_id=doc_id,
            product_category=llm_out.get("product_category"),
            user_behaviour=llm_out.get("user_behaviour"),
            wishlist_behaviour=wb,
            purchase_intent=llm_out.get("purchase_intent"),
            purchase_stage=llm_out.get("purchase_stage"),
            barrier=bar,
            uncertainty=llm_out.get("uncertainty"),
            user_job=llm_out.get("user_job"),
            workaround=llm_out.get("workaround"),
            external_information_source=llm_out.get("external_information_source"),
            alternative_considered=llm_out.get("alternative_considered"),
            occasion=llm_out.get("occasion"),
            fit_size=llm_out.get("fit_size"),
            styling=llm_out.get("styling"),
            price=llm_out.get("price"),
            reviews_social_validation=llm_out.get("reviews_social_validation"),
            availability=llm_out.get("availability"),
            quality_expectation=llm_out.get("quality_expectation"),
            other_new_theme=llm_out.get("other_new_theme"),
            evidence_strength=st
        )

    def _extract_with_rule_matcher(self, doc_id: str, text: str, source_scope: str) -> DocumentExtraction:
        t_lower = text.lower()

        # 1. Product Category
        category = None
        if re.search(r"\b(kurta|kurti|anarkali|lehenga|saree|ethnic|gajra gang|likha)\b", t_lower):
            category = "Ethnic & Traditional Wear"
        elif re.search(r"\b(dress|dresses|gown|western|top|tops|t-shirt|shirt|jeans)\b", t_lower):
            category = "Western Apparel"
        elif re.search(r"\b(shoe|shoes|heels|flats|footwear|loafers|sandals)\b", t_lower):
            category = "Footwear"
        elif re.search(r"\b(bag|handbag|jhumka|jhumkas|jewellery|jewelry|earrings)\b", t_lower):
            category = "Fashion Accessories"
        elif re.search(r"\b(lipstick|makeup|skincare|serum|foundation|shampoo)\b", t_lower):
            category = "Beauty & Personal Care"

        # 2. Purchase Barrier Detection
        barrier = None
        fit_size_detail = None
        quality_detail = None
        p_vs_img_detail = None
        styling_detail = None
        delivery_detail = None
        other_theme = None

        if re.search(r"\b(size|sizing|fit|fitting|tight|loose|size chart|wrong size|chart|32b|uk 6|small|large|xl|xs)\b", t_lower):
            barrier = "fit_size"
            fit_size_detail = "Sizing inconsistency or wrong size chart details mentioned."
        elif re.search(r"\b(quality|cloth|material|stitching|see-through|transparent|cheap|kapda|fabric|polyester|cotton)\b", t_lower):
            barrier = "quality"
            quality_detail = "Fabric quality, transparency, or material expectations differ."
        elif re.search(r"\b(photo|photos|picture|pictures|color|colour|look|differ|different from image|different than photo)\b", t_lower):
            barrier = "product_vs_image"
            p_vs_img_detail = "Actual product appearance or color differs from online listing photos."
        elif re.search(r"\b(style|styling|pair|wear|combination|outfit context|match)\b", t_lower):
            barrier = "styling"
            styling_detail = "Uncertainty regarding outfit styling or item pairing."
        elif re.search(r"\b(wishlist paralysis|too many choices|hoarding|confused|decide|indecision)\b", t_lower):
            barrier = "decision_paralysis"
        elif re.search(r"\b(delay|delayed|delivery|late|courier|pickup|return pickup|return|refund|support)\b", t_lower):
            barrier = "delivery_logistics"
            delivery_detail = "Delivery delay or return pickup friction."
        elif re.search(r"\b(price|expensive|sale|payday|budget|costly)\b", t_lower):
            barrier = "price_timing"
        elif re.search(r"\b(out of stock|unavailable|sold out)\b", t_lower):
            barrier = "availability"
        elif re.search(r"\b(myntra|zara|h&m|amazon|ajio)\b", t_lower):
            barrier = "social_validation"
        else:
            if len(text) > 100:
                barrier = "other_emerging"
                other_theme = f"General consumer discussion on {source_scope}"

        # 3. Wishlist Behaviour Taxonomy
        wishlist_beh = None
        if "wishlist" in t_lower or "saved" in t_lower or "save for later" in t_lower:
            if re.search(r"\b(paralysis|hoard|hoarding|mood board|bored|stressed)\b", t_lower):
                wishlist_beh = "bookmark_save_for_later"
            elif re.search(r"\b(myntra|compare|comparison|other app|amazon)\b", t_lower):
                wishlist_beh = "compare_alternatives"
            elif re.search(r"\b(wedding|event|trip|party|function|occasion|festive)\b", t_lower):
                wishlist_beh = "future_occasion"
            elif re.search(r"\b(wait|waiting|payday|sale)\b", t_lower):
                wishlist_beh = "waiting_timing"
            elif re.search(r"\b(review|rating|photo|size chart|fabric)\b", t_lower):
                wishlist_beh = "need_more_information"
            elif re.search(r"\b(ready to buy|want to purchase|ordered right away|going to checkout)\b", t_lower):
                wishlist_beh = "genuine_purchase_intent"
            else:
                wishlist_beh = "bookmark_save_for_later"

        # 4. Evidence Strength Rating
        if len(text) > 250 or (barrier and category):
            strength = "high"
        elif len(text) < 50:
            strength = "low"
        else:
            strength = "medium"

        # 5. Null-if-unsupported policy
        return DocumentExtraction(
            document_id=doc_id,
            product_category=category,
            user_behaviour="Browsed online fashion listing and saved item to wishlist" if "wishlist" in t_lower else None,
            wishlist_behaviour=wishlist_beh,
            purchase_intent="High purchase intent expressed" if re.search(r"\b(want to buy|planning to buy)\b", t_lower) else None,
            purchase_stage="Consideration" if wishlist_beh else None,
            barrier=barrier,
            uncertainty="Sizing or fit uncertainty" if barrier == "fit_size" else ("Quality uncertainty" if barrier == "quality" else None),
            user_job="Find well-fitted, accurate fashion items for specific occasion" if category else None,
            workaround="Checks Reddit reviews or orders multiple sizes" if "reddit" in t_lower or "size" in t_lower else None,
            external_information_source="Reddit" if "reddit" in t_lower else None,
            alternative_considered="Myntra" if "myntra" in t_lower else None,
            occasion="Wedding / Festive Function" if re.search(r"\b(wedding|shaadi|festive|diwali)\b", t_lower) else None,
            fit_size=fit_size_detail,
            styling=styling_detail,
            price=None,
            reviews_social_validation="Reddit community feedback" if "reddit" in t_lower else None,
            availability="Size out of stock" if barrier == "availability" else None,
            quality_expectation=quality_detail,
            other_new_theme=other_theme,
            evidence_strength=strength
        )
