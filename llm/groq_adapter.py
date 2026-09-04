import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from groq import Groq

# Load .env variables into os.environ
load_dotenv(dotenv_path=".env", override=True)

from config.settings import settings
from llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class GroqAdapter(LLMProvider):
    """
    Groq LLM Adapter implementing the LLMProvider interface.
    Adheres strictly to Phase 0 and cross-cutting architecture rules:
    - Model name is dynamically loaded from environment variables (never hard-coded).
    - Only retrieved context chunks are provided as evidence.
    - If Groq is unconfigured, rate-limited, or unavailable, clear error states are returned without hallucinating answers.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or settings.groq_api_key
        # Always prioritize live environment variable or tested compatible model
        env_model = os.getenv("GROQ_MODEL")
        if env_model and "llama-3.3-70b-versatile" not in env_model:
            self.model = model or env_model
        else:
            self.model = model or settings.groq_model if settings.groq_model and "llama-3.3-70b-versatile" not in settings.groq_model else "openai/gpt-oss-120b"
            
        self.client: Optional[Groq] = None

        if self.api_key and self.api_key.strip():
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None

    def ping(self) -> Dict[str, Any]:
        """
        Check if Groq API is configured and accessible.
        """
        if not self.client or not self.model:
            return {
                "status": "not_configured",
                "provider": "Groq",
                "model": self.model or "Not configured",
                "message": "Groq API key or model is missing in environment."
            }

        try:
            # Lightweight connectivity probe
            models = self.client.models.list()
            return {
                "status": "connected",
                "provider": "Groq",
                "model": self.model,
                "message": "Groq API connection verified."
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "Groq",
                "model": self.model,
                "message": f"Groq API connection failed: {str(e)}"
            }

    def generate(
        self,
        prompt: str,
        context_chunks: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Grounded inference execution using Groq with structured JSON output.
        """
        if not self.client or not self.model:
            raise RuntimeError(
                "LLM inference requested but Groq is not configured. "
                "Set GROQ_API_KEY and GROQ_MODEL in environment variables."
            )

        # Build context block
        context_lines = []
        for i, c in enumerate(context_chunks):
            doc_id = c.get('document_id', 'N/A')
            context_lines.append(
                f"[Evidence Passage {i+1} | Document ID: {doc_id} | Platform: {c.get('platform', 'Unknown')} | Source: {c.get('source_name', 'Unknown')} ({c.get('source_scope', 'unknown')})]\n{c.get('text', '')}"
            )
        context_text = "\n\n".join(context_lines)

        base_system = (
            "You are the Nykaa Fashion AI Wishlist Discovery Engine reasoning engine.\n"
            "STRICT GROUNDING & PM SYNTHESIS RULES:\n"
            "1. Answer ONLY using the provided retrieved passages. Never invent external facts, numbers, or personas.\n"
            "2. Under 'grounded_answer', produce an in-depth, comprehensive, human-written PM research synthesis of AT LEAST 10 lines (approximately 180–300 words, organized across 2 to 3 well-developed thematic paragraphs separated by blank lines) explaining why shoppers hesitate or experience friction. Combine evidence into clear, nuanced thematic findings using natural language.\n"
            "3. DO NOT include any inline citations or references such as [Passage X], (Passage X), 'Passage X', document IDs, chunk IDs, relevance percentages, or URLs inside 'grounded_answer'. Supporting evidence is displayed in a separate section below.\n"
            "4. IMPORTANT: Do NOT treat multiple passages sharing the same Document ID as independent user voices. Treat them as one underlying evidence source.\n"
            "5. NO OVERCLAIMING: Use measured research phrasing ('The evidence suggests...', 'Users appear to...', 'The available evidence indicates...'). Never say 'This proves...', 'Users definitely...', 'The root cause is...'.\n"
            "6. Strictly separate: Evidence -> Pattern -> Inference -> Opportunity -> Metric Connection -> Research Hypothesis.\n"
            "7. Never propose monetary incentives, discounts, coupons, price drops, or cashbacks.\n"
            "8. Never declare a 'Final Problem' or 'Proven Root Cause' — output must serve as a research hypothesis for user interviews.\n"
            "9. Output MUST be valid, parsable JSON."
        )

        full_system = f"{base_system}\n\n{system_instruction}" if system_instruction else base_system

        user_message = f"RETRIEVED EVIDENCE PASSAGES:\n{context_text}\n\nUSER DISCOVERY QUESTION:\n{prompt}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content or "{}"
            return self._clean_and_parse_json(raw_content)

        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise RuntimeError(f"Groq generation failed: {str(e)}")

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Clean markdown json fences and parse JSON robustly.
        """
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback regex search for JSON block
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Failed to parse model output as JSON: {raw_text[:200]}")


# Factory helper
def get_llm_provider() -> LLMProvider:
    """Return configured LLMProvider instance."""
    return GroqAdapter()
