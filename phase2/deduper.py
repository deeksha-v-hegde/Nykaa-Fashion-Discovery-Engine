import hashlib
import re
from typing import Dict, List, Optional, Set


class NearDuplicateDetector:
    """
    Phase 2 Near-Duplicate Detector with Inverted Index Acceleration.
    Detects identical and near-identical reviews/posts (e.g. repeated spam, copy-paste templates)
    using word n-gram Jaccard similarity and normalized shingling.
    
    Rather than deleting duplicates, it marks `duplicate_of = canonical_doc_id`
    to maintain a strict audit trail and avoid double-counting in later statistical rollups.
    """

    def __init__(self, jaccard_threshold: float = 0.85, shingle_k: int = 3):
        self.jaccard_threshold = jaccard_threshold
        self.shingle_k = shingle_k
        self._seen_exact_hashes: Dict[str, str] = {}  # norm_hash -> doc_id
        self._doc_shingles: Dict[str, Set[str]] = {}  # doc_id -> shingle_set
        self._shingle_index: Dict[str, Set[str]] = {}  # shingle -> set of doc_ids

    def _compute_shingles(self, text: str) -> Set[str]:
        words = re.findall(r"\b\w+\b", text.lower())
        if len(words) < self.shingle_k:
            return set(words)
        return {" ".join(words[i:i + self.shingle_k]) for i in range(len(words) - self.shingle_k + 1)}

    def check_and_register(self, doc_id: str, cleaned_text: str) -> Optional[str]:
        """
        Checks if the document is an exact or near duplicate of any previously registered document.
        Uses an inverted index to only evaluate candidate documents sharing shingles.
        """
        if not cleaned_text:
            return None

        # 1. Exact normalized hash check
        norm_hash = hashlib.sha256(cleaned_text.lower().encode("utf-8")).hexdigest()
        if norm_hash in self._seen_exact_hashes:
            return self._seen_exact_hashes[norm_hash]

        # 2. Inverted Index Near-duplicate Jaccard check
        shingles = self._compute_shingles(cleaned_text)
        if len(shingles) >= 4:
            # Find candidate docs that share at least one shingle
            candidate_doc_counts: Dict[str, int] = {}
            for sh in shingles:
                for cand_id in self._shingle_index.get(sh, ()):
                    candidate_doc_counts[cand_id] = candidate_doc_counts.get(cand_id, 0) + 1

            # Only check candidates with high shared shingle count
            min_shared = int(len(shingles) * self.jaccard_threshold * 0.7)
            for cand_id, shared_cnt in candidate_doc_counts.items():
                if shared_cnt >= min_shared:
                    cand_shingles = self._doc_shingles[cand_id]
                    intersection = len(shingles.intersection(cand_shingles))
                    union = len(shingles.union(cand_shingles))
                    if union > 0 and (intersection / union) >= self.jaccard_threshold:
                        return cand_id

        # Register document
        self._seen_exact_hashes[norm_hash] = doc_id
        if len(shingles) >= 4:
            self._doc_shingles[doc_id] = shingles
            for sh in shingles:
                if sh not in self._shingle_index:
                    self._shingle_index[sh] = set()
                self._shingle_index[sh].add(doc_id)

        return None
