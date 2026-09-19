from __future__ import annotations

from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class TranscriptRetriever:
    """
    Dense retriever for transcript chunks using
    BGE embeddings + FAISS.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
    ) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        self.chunks: list[dict[str, Any]] = []
        self.index: faiss.Index | None = None

    def build_index(self, chunks: list[dict[str, Any]]) -> None:
        """
        Generate embeddings for all chunks and build a FAISS index.
        """
        if not chunks:
            raise ValueError("No chunks provided.")

        self.chunks = chunks

        texts = [chunk["retrieval_text"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        embeddings = np.asarray(embeddings, dtype="float32")

        dimension = embeddings.shape[1]

        # Inner product on normalized vectors = cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the top-k most relevant transcript chunks.
        """
        if self.index is None:
            raise RuntimeError("FAISS index has not been built yet.")

        if not query.strip():
            return []

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks)),
        )

        results: list[dict[str, Any]] = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            chunk = dict(self.chunks[index])
            chunk["score"] = float(score)

            results.append(chunk)

        return results