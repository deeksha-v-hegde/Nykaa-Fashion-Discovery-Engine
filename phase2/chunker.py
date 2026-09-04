import re
from dataclasses import dataclass
from typing import List, Optional
from config.settings import Settings


@dataclass
class ChunkDraft:
    chunk_id: str
    document_id: str
    ordinal: int
    text: str
    token_count: int
    source_scope: str
    source_id: str
    embedding_version: Optional[str] = None


class DocumentChunker:
    """
    Phase 2 Document Chunker.
    Splits cleaned, relevant documents into retrieval-friendly chunks using sentence-aware
    sliding window chunking based on configured `chunk_size` and `chunk_overlap`.
    
    Generates deterministic, stable `chunk_id`s in format: `chk_{doc_id}_{ordinal}`.
    """

    SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+|\n\n+")

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        settings = Settings()
        self.chunk_size = chunk_size or settings.chunk_size  # e.g. 400 characters (~80-100 tokens)
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap  # e.g. 50 characters

    def _estimate_tokens(self, text: str) -> int:
        """Estimates token count (approximately 1 token per 4 characters or word count)."""
        words = len(text.split())
        char_estimate = max(1, len(text) // 4)
        return max(words, char_estimate)

    def chunk_document(
        self,
        document_id: str,
        cleaned_text: str,
        source_scope: str,
        source_id: str
    ) -> List[ChunkDraft]:
        """
        Chunks a single document into one or more ChunkDraft instances.
        Short documents under chunk_size are preserved as a single high-fidelity chunk.
        Long documents are split across sentence boundaries with sliding overlap.
        """
        if not cleaned_text or not cleaned_text.strip():
            return []

        text = cleaned_text.strip()
        chunks: List[ChunkDraft] = []

        # If document fits within chunk_size, output single chunk
        if len(text) <= self.chunk_size:
            chunks.append(ChunkDraft(
                chunk_id=f"chk_{document_id}_0",
                document_id=document_id,
                ordinal=0,
                text=text,
                token_count=self._estimate_tokens(text),
                source_scope=source_scope,
                source_id=source_id
            ))
            return chunks

        # Sentence-aware sliding window for longer documents
        sentences = [s.strip() for s in self.SENTENCE_SPLIT_REGEX.split(text) if s.strip()]
        if not sentences:
            sentences = [text]

        current_sentences: List[str] = []
        current_len = 0
        ordinal = 0

        for s in sentences:
            s_len = len(s)
            if current_len + s_len > self.chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences).strip()
                chunks.append(ChunkDraft(
                    chunk_id=f"chk_{document_id}_{ordinal}",
                    document_id=document_id,
                    ordinal=ordinal,
                    text=chunk_text,
                    token_count=self._estimate_tokens(chunk_text),
                    source_scope=source_scope,
                    source_id=source_id
                ))
                ordinal += 1

                # Retain overlap sentences from the end
                overlap_sentences: List[str] = []
                overlap_len = 0
                for prev_s in reversed(current_sentences):
                    if overlap_len + len(prev_s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, prev_s)
                        overlap_len += len(prev_s)
                    else:
                        break

                current_sentences = overlap_sentences + [s]
                current_len = sum(len(x) for x in current_sentences) + len(current_sentences)
            else:
                current_sentences.append(s)
                current_len += s_len + 1

        # Emit remaining sentences if any
        if current_sentences:
            chunk_text = " ".join(current_sentences).strip()
            # Avoid duplicate if identical to prior chunk
            if not chunks or chunks[-1].text != chunk_text:
                chunks.append(ChunkDraft(
                    chunk_id=f"chk_{document_id}_{ordinal}",
                    document_id=document_id,
                    ordinal=ordinal,
                    text=chunk_text,
                    token_count=self._estimate_tokens(chunk_text),
                    source_scope=source_scope,
                    source_id=source_id
                ))

        return chunks
