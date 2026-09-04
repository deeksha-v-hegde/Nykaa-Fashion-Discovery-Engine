import html
import re
import unicodedata
from typing import Optional


class TextNormalizer:
    """
    Phase 2 Normalizer.
    Cleans raw text from reviews and community discussions while strictly preserving:
    - User intent, sentiment, and tone
    - Sizing numbers and apparel fit indicators (e.g. XS, S, M, L, XL, XXL, 32B, 34, UK 6)
    - Currency and price mentions (e.g. ₹, Rs., INR 2499)
    - Hinglish terminology commonly used in Indian fashion shopping (e.g. kurta, dupatta, jhumkas, kapda, mehenga, sahi)
    """

    # Boilerplate patterns to strip (e.g. App Store / Play Store web artifacts)
    BOILERPLATE_PATTERNS = [
        re.compile(r"read\s+more\s*\.{0,3}", re.IGNORECASE),
        re.compile(r"translate\s+review", re.IGNORECASE),
        re.compile(r"original\s+review\s*\(.*?\)", re.IGNORECASE),
        re.compile(r"was\s+this\s+review\s+helpful\?.*", re.IGNORECASE),
        re.compile(r"report\s+abuse", re.IGNORECASE),
        re.compile(r"\[deleted\]", re.IGNORECASE),
        re.compile(r"\[removed\]", re.IGNORECASE),
    ]

    # Excessive whitespace / newline patterns
    REPEATED_NEWLINES = re.compile(r"\n{3,}")
    REPEATED_SPACES = re.compile(r"[ \t]{2,}")
    REPEATED_PUNCTUATION = re.compile(r"([!?.,])\1{3,}")

    @classmethod
    def normalize(cls, text: Optional[str]) -> str:
        """
        Normalizes raw input text into clean, canonical text.
        """
        if not text:
            return ""

        # 1. Unicode NFKC normalization
        cleaned = unicodedata.normalize("NFKC", text)

        # 2. Decode HTML entities (e.g. &amp;, &quot;, &#39;, &lt;, &gt;)
        cleaned = html.unescape(cleaned)

        # 3. Strip non-printable/control characters (preserve standard newlines and tabs)
        cleaned = "".join(ch for ch in cleaned if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C"))

        # 4. Remove UI boilerplate artifacts
        for pat in cls.BOILERPLATE_PATTERNS:
            cleaned = pat.sub(" ", cleaned)

        # 5. Normalize repeated exclamation/question marks (e.g. "??????" -> "??")
        cleaned = cls.REPEATED_PUNCTUATION.sub(r"\1\1", cleaned)

        # 6. Normalize whitespace
        cleaned = cls.REPEATED_SPACES.sub(" ", cleaned)
        cleaned = cls.REPEATED_NEWLINES.sub("\n\n", cleaned)

        return cleaned.strip()
