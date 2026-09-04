import logging
from typing import Any, Dict
from phase4.ask_engine import AskEngine
from phase11.models import ChaosTestResult

logger = logging.getLogger("phase11.chaos_tester")


class ChaosTester:
    """
    Phase 11 Chaos Tester.
    Simulates Groq API outage / invalid API key to verify zero-crash deterministic fallback.
    """

    @staticmethod
    def test_groq_outage_fallback() -> ChaosTestResult:
        logger.info("Executing Chaos Test: Simulating Groq API outage / unconfigured key...")

        # Initialize AskEngine (offline mode)
        engine = AskEngine()
        # Force groq_adapter to unconfigured state for chaos test
        original_key = engine.groq_adapter.api_key
        engine.groq_adapter.api_key = None

        test_query = "What causes users to postpone fashion purchases?"

        try:
            res = engine.ask(query=test_query)

            # Verify response is valid and non-crashing
            passed = (
                res.status in ("success", "refusal", "insufficient_evidence")
                and len(res.grounded_answer) > 0
                and len(res.evidence) > 0
                and res.metric_connection.thirty_day_conversion == "unknown"
            )

            # Restore original key
            engine.groq_adapter.api_key = original_key

            return ChaosTestResult(
                test_name="Groq Outage Chaos Test",
                simulated_failure="GROQ_API_KEY unconfigured / API outage",
                expected_fallback="Deterministic grounded vector fallback (_generate_structured_fallback)",
                actual_outcome=f"Status: {res.status} | Returned {len(res.evidence)} verbatim cited chunks",
                passed=passed,
                details={
                    "grounded_answer_length": len(res.grounded_answer),
                    "citations_count": len(res.evidence),
                    "confidence_rating": res.confidence
                }
            )
        except Exception as e:
            engine.groq_adapter.api_key = original_key
            logger.error(f"Chaos test failed with exception: {e}")
            return ChaosTestResult(
                test_name="Groq Outage Chaos Test",
                simulated_failure="GROQ_API_KEY unconfigured / API outage",
                expected_fallback="Deterministic grounded vector fallback",
                actual_outcome=f"Exception raised: {str(e)}",
                passed=False
            )
