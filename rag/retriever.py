from __future__ import annotations

from typing import Any

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class TranscriptRetriever:
    """
    Hybrid retriever for expert interview transcripts.

    Uses:
    - Sentence Transformers + FAISS for semantic retrieval
    - BM25 for keyword retrieval
    - Reciprocal Rank Fusion (RRF) for combining results

    Supports filtering by expert or market.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        self.chunks: list[dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None

        self.faiss_index: faiss.Index | None = None
        self.bm25: BM25Okapi | None = None

        self.tokenized_documents: list[list[str]] = []

    def build_index(self, chunks: list[dict[str, Any]]) -> None:
        """Build FAISS and BM25 indexes."""

        if not chunks:
            raise ValueError("No chunks provided.")

        self.chunks = chunks

        texts = [
            chunk["retrieval_text"]
            for chunk in chunks
        ]

        # Dense embeddings
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        self.embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = self.embeddings.shape[1]

        self.faiss_index = faiss.IndexFlatIP(dimension)
        self.faiss_index.add(self.embeddings)

        # BM25
        self.tokenized_documents = [
            self._tokenize(text)
            for text in texts
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple lowercase tokenizer."""
        return text.lower().split()

    @staticmethod
    def _rrf_score(
        rank: int,
        k: int = 60,
    ) -> float:
        """Reciprocal Rank Fusion score."""
        return 1.0 / (k + rank)

    def search(
        self,
        query: str,
        top_k: int = 5,
        market: str | None = None,
        expert: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search transcript chunks.

        Optional filters:
        - market
        - expert

        This allows the application to answer the same
        interview question separately for each expert.
        """

        if not query.strip():
            return []

        if self.embeddings is None or self.bm25 is None:
            raise RuntimeError(
                "Retriever index has not been built."
            )

        # ---------------------------------------------
        # 1. Determine eligible chunks
        # ---------------------------------------------
        eligible_indices: list[int] = []

        for index, chunk in enumerate(self.chunks):

            if market is not None:
                if chunk["market"].strip().lower() != market.strip().lower():
                    continue

            if expert is not None:
                if chunk["expert"].strip().lower() != expert.strip().lower():
                    continue

            eligible_indices.append(index)

        if not eligible_indices:
            return []

        # ---------------------------------------------
        # 2. Dense scores
        # ---------------------------------------------
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        eligible_embeddings = self.embeddings[
            eligible_indices
        ]

        dense_scores = (
            eligible_embeddings @ query_embedding[0]
        )

        dense_order = np.argsort(
            dense_scores
        )[::-1]

        dense_ranked = [
            eligible_indices[int(i)]
            for i in dense_order[:top_k]
        ]

        # ---------------------------------------------
        # 3. BM25 scores
        # ---------------------------------------------
        query_tokens = self._tokenize(query)

        all_bm25_scores = self.bm25.get_scores(
            query_tokens
        )

        eligible_bm25_scores = np.array(
            [
                all_bm25_scores[index]
                for index in eligible_indices
            ]
        )

        bm25_order = np.argsort(
            eligible_bm25_scores
        )[::-1]

        bm25_ranked = [
            eligible_indices[int(i)]
            for i in bm25_order[:top_k]
        ]

        # ---------------------------------------------
        # 4. Reciprocal Rank Fusion
        # ---------------------------------------------
        combined_scores: dict[int, float] = {}

        for rank, index in enumerate(
            dense_ranked,
            start=1,
        ):
            combined_scores[index] = (
                combined_scores.get(index, 0.0)
                + self._rrf_score(rank)
            )

        for rank, index in enumerate(
            bm25_ranked,
            start=1,
        ):
            combined_scores[index] = (
                combined_scores.get(index, 0.0)
                + self._rrf_score(rank)
            )

        # ---------------------------------------------
        # 5. Final ranking
        # ---------------------------------------------
        ranked_results = sorted(
            combined_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        results: list[dict[str, Any]] = []

        for index, score in ranked_results[:top_k]:
            result = dict(self.chunks[index])

            result["retrieval_score"] = float(score)

            results.append(result)

        return results