import hashlib
import logging
import os
from pathlib import Path
from typing import List, Optional, Union
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from config.settings import Settings

logger = logging.getLogger("phase3.embedder")
MODEL_DIR = Path("data/vector_store")


class TextEmbedder:
    """
    Phase 3 Text Embedder.
    Generates normalized 384-dimensional dense semantic vectors using
    TF-IDF with Latent Semantic Analysis (LSA / TruncatedSVD) projection.
    
    Ensures:
    - Fixed 384-dimension vector output.
    - L2-normalized vectors (unit length) for direct cosine dot-product retrieval.
    - Persistent projection matrix saved to disk for consistent incremental query encoding.
    - Configurable model version identifier from Settings (EMBEDDING_MODEL).
    """

    DEFAULT_DIM = 384
    MODEL_ARTIFACT = MODEL_DIR / "lsa_embedder_v1.joblib"

    def __init__(self, model_name: Optional[str] = None, dim: int = DEFAULT_DIM):
        settings = Settings()
        self.model_name = model_name or settings.embedding_model or "tfidf-lsa-384"
        self.dim = dim
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd: Optional[TruncatedSVD] = None
        self._is_fitted = False
        self._load_or_init()

    def _load_or_init(self):
        """Loads cached projection models from disk if available."""
        if self.MODEL_ARTIFACT.exists():
            try:
                state = joblib.load(self.MODEL_ARTIFACT)
                self.vectorizer = state["vectorizer"]
                self.svd = state["svd"]
                self.model_name = state.get("model_name", self.model_name)
                self.dim = state.get("dim", self.dim)
                self._is_fitted = True
                logger.info(f"Loaded existing embedding projection matrix from {self.MODEL_ARTIFACT}")
            except Exception as e:
                logger.warning(f"Could not load cached projection matrix: {e}. Will re-fit.")

    def fit(self, texts: List[str]):
        """
        Fits the TF-IDF vocabulary and SVD projection matrix on the corpus text.
        """
        if not texts:
            return

        logger.info(f"Fitting embedding vocabulary and SVD projection matrix on {len(texts)} chunks...")
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=25000,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        tfidf_matrix = self.vectorizer.fit_transform(texts)

        n_components = min(self.dim, tfidf_matrix.shape[1] - 1, tfidf_matrix.shape[0] - 1)
        if n_components < self.dim:
            self.dim = max(16, n_components)

        self.svd = TruncatedSVD(n_components=self.dim, random_state=42)
        self.svd.fit(tfidf_matrix)
        self._is_fitted = True

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "svd": self.svd,
            "model_name": self.model_name,
            "dim": self.dim
        }, self.MODEL_ARTIFACT)
        logger.info(f"Saved embedding projection matrix (dim={self.dim}) to {self.MODEL_ARTIFACT}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encodes a list of texts into dense 384-dim normalized float32 vectors.
        Shape: (len(texts), dim)
        """
        if not texts:
            return np.empty((0, self.dim), dtype=np.float32)

        if not self._is_fitted:
            self.fit(texts)

        tfidf_matrix = self.vectorizer.transform(texts)
        dense_vecs = self.svd.transform(tfidf_matrix).astype(np.float32)

        # L2-normalize vectors for fast cosine dot products
        norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        normalized_vecs = dense_vecs / norms
        return normalized_vecs

    def embed_query(self, query: str) -> np.ndarray:
        """
        Encodes a single query text into a 1D normalized float32 vector.
        Shape: (dim,)
        """
        vecs = self.embed_texts([query])
        return vecs[0]
