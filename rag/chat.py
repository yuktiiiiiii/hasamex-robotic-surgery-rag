from __future__ import annotations

from typing import Any

from .chunks import create_chunks
from .generator import TranscriptGenerator
from .parser import parse_multiple_transcripts
from .retriever import TranscriptRetriever


class TranscriptChat:
    """
    Ask free-form questions across all expert transcripts.

    The answer is generated only from retrieved transcript evidence,
    while exact quotes and timestamps come directly from source chunks.
    """

    def __init__(self, data_folder: str = "data") -> None:
        self.data_folder = data_folder

        # Load transcripts
        self.turns = parse_multiple_transcripts(
            data_folder
        )

        # Create expert-only chunks
        self.chunks = create_chunks(
            self.turns
        )

        # Build hybrid retriever
        self.retriever = TranscriptRetriever()
        self.retriever.build_index(
            self.chunks
        )

        # Answer generator
        self.generator = TranscriptGenerator()

    def ask(
        self,
        question: str,
        top_k: int = 6,
    ) -> dict[str, Any]:
        """
        Ask a question across all transcripts.
        """

        if not question.strip():
            return {
                "question": question,
                "answer": (
                    "Please enter a question."
                ),
                "sources": [],
            }

        # Search across ALL markets.
        retrieved_chunks = self.retriever.search(
            query=question,
            top_k=top_k,
        )

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": (
                    "The transcripts do not provide enough "
                    "information to answer this."
                ),
                "sources": [],
            }

        answer = self.generator.generate_answer(
            question=question,
            chunks=retrieved_chunks,
        )

        sources = self.generator.build_sources(
            retrieved_chunks
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }