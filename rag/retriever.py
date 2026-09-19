from __future__ import annotations

from typing import Any

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class TranscriptRetriever:
    """
    Hybrid retriever for expert interview transcripts.

    Retrieval pipeline:
    1. Dense semantic retrieval using Sentence Transformers + FAISS
    2. BM25 keyword retrieval
    3. Reciprocal Rank Fusion (RRF)
    4. Dense relevance gate to reject weak/irrelevant matches

    Supports optional filtering by market or expert.
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

    def build_index(
        self,
        chunks: list[dict[str, Any]],
    ) -> None:
        """Build FAISS and BM25 indexes."""

        if not chunks:
            raise ValueError("No chunks provided.")

        self.chunks = chunks

        texts = [
            chunk["retrieval_text"]
            for chunk in chunks
        ]

        # -------------------------------------------------
        # Dense embeddings
        # -------------------------------------------------
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

        # Inner product on normalized vectors
        # is equivalent to cosine similarity.
        self.faiss_index = faiss.IndexFlatIP(
            dimension
        )

        self.faiss_index.add(
            self.embeddings
        )

        # -------------------------------------------------
        # BM25
        # -------------------------------------------------
        self.tokenized_documents = [
            self._tokenize(text)
            for text in texts
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

    @staticmethod
    def _tokenize(
        text: str,
    ) -> list[str]:
        """Simple lowercase tokenizer."""
        return text.lower().split()

    @staticmethod
    def _rrf_score(
        rank: int,
        k: int = 60,
    ) -> float:
        """
        Reciprocal Rank Fusion score.

        rank starts at 1.
        """
        return 1.0 / (k + rank)

    def search(
        self,
        query: str,
        top_k: int = 5,
        market: str | None = None,
        expert: str | None = None,
        min_dense_score: float = 0.35,
    ) -> list[dict[str, Any]]:
        """
        Search transcript chunks using hybrid retrieval.

        A dense similarity threshold is applied before BM25/RRF,
        which helps prevent unrelated questions from being
        passed to the answer generator.
        """

        if not query.strip():
            return []

        if (
            self.embeddings is None
            or self.bm25 is None
            or self.faiss_index is None
        ):
            raise RuntimeError(
                "Retriever index has not been built."
            )

        # -------------------------------------------------
        # 1. Determine eligible chunks
        # -------------------------------------------------
        eligible_indices: list[int] = []

        for index, chunk in enumerate(self.chunks):

            if market is not None:
                if (
                    chunk["market"]
                    .strip()
                    .lower()
                    != market.strip().lower()
                ):
                    continue

            if expert is not None:
                if (
                    chunk["expert"]
                    .strip()
                    .lower()
                    != expert.strip().lower()
                ):
                    continue

            eligible_indices.append(index)

        if not eligible_indices:
            return []

        # -------------------------------------------------
        # 2. Query embedding
        # -------------------------------------------------
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        # -------------------------------------------------
        # 3. Dense similarity scores
        # -------------------------------------------------
        eligible_embeddings = self.embeddings[
            eligible_indices
        ]

        dense_scores = (
            eligible_embeddings
            @ query_embedding[0]
        )

        # -------------------------------------------------
        # 4. Dense relevance gate
        # -------------------------------------------------
        # Keep only chunks that are semantically relevant
        # enough to the question.
        relevant_indices: list[int] = []

        dense_score_map: dict[int, float] = {}

        for position, score in enumerate(
            dense_scores
        ):
            index = eligible_indices[position]
            score = float(score)

            if score >= min_dense_score:
                relevant_indices.append(index)
                dense_score_map[index] = score

        # No sufficiently relevant evidence.
        if not relevant_indices:
            return []

        # -------------------------------------------------
        # 5. Rank relevant chunks using dense retrieval
        # -------------------------------------------------
        dense_ranked = sorted(
            relevant_indices,
            key=lambda index: dense_score_map[index],
            reverse=True,
        )

        dense_ranked = dense_ranked[:top_k]

        # -------------------------------------------------
        # 6. BM25 retrieval
        # -------------------------------------------------
        query_tokens = self._tokenize(query)

        all_bm25_scores = self.bm25.get_scores(
            query_tokens
        )

        # IMPORTANT:
        # BM25 is restricted to chunks that already passed
        # the dense relevance gate. This prevents unrelated
        # chunks from coming back just because of a keyword.
        bm25_ranked = sorted(
            relevant_indices,
            key=lambda index: float(
                all_bm25_scores[index]
            ),
            reverse=True,
        )[:top_k]

        # -------------------------------------------------
        # 7. Reciprocal Rank Fusion
        # -------------------------------------------------
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

        # -------------------------------------------------
        # 8. Final ranking
        # -------------------------------------------------
        ranked_results = sorted(
            combined_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        # -------------------------------------------------
        # 9. Build result objects
        # -------------------------------------------------
        results: list[dict[str, Any]] = []

        for index, rrf_score in ranked_results[:top_k]:

            result = dict(
                self.chunks[index]
            )

            result["retrieval_score"] = float(
                rrf_score
            )

            result["dense_score"] = float(
                dense_score_map[index]
            )

            result["bm25_score"] = float(
                all_bm25_scores[index]
            )

            results.append(result)

        return results