import logging
from typing import List, Optional
from phase3.retriever import SearchResult, VectorRetriever
from phase7.models import OpportunityCitation

logger = logging.getLogger("phase7.evidence_picker")


class EvidencePicker:
    """
    Phase 7 Evidence Citation Picker.
    Retrieves the 3-5 strongest supporting evidence chunks for an opportunity candidate.
    """

    def __init__(self, embedding_model: Optional[str] = None):
        self.retriever = VectorRetriever(embedding_model=embedding_model)

    def pick_citations(self, query: str, top_k: int = 4) -> List[OpportunityCitation]:
        results: List[SearchResult] = self.retriever.search(query=query, top_k=top_k)

        citations = []
        for r in results:
            citations.append(OpportunityCitation(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                snippet=r.text,
                source_name=r.source_name,
                source_scope=r.source_scope,
                published_at=r.published_at,
                url=r.url
            ))
        return citations
