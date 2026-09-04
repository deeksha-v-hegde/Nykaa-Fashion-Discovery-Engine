from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    """
    Abstract LLM Provider Interface.
    All inference calls must strictly pass through this interface.
    The LLM receives only retrieved or document-local text, never 'answer from general knowledge'.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        context_chunks: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response from grounded context chunks.

        :param prompt: User/Discovery question or task instruction.
        :param context_chunks: List of retrieved evidence chunk dictionaries.
        :param system_instruction: Strict grounding rules & constraints.
        :param json_schema: Optional expected JSON structure.
        :return: Parsed dictionary response.
        """
        pass

    @abstractmethod
    def ping(self) -> Dict[str, Any]:
        """
        Connectivity check without generating ungrounded facts.
        :return: Status dictionary with model name and availability.
        """
        pass
