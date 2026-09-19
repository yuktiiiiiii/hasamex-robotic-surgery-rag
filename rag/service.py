from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .chunks import create_chunks
from .comparison import (
    identify_common_themes,
    identify_differences,
)
from .generator import TranscriptGenerator
from .guide import INTERVIEW_GUIDE
from .guide_mapper import map_guide_questions
from .parser import parse_multiple_transcripts
from .qa_pairs import build_qa_pairs
from .retriever import TranscriptRetriever


class TranscriptService:
    """
    Main application service.

    Responsibilities:
    - Load transcript files
    - Parse speaker/timestamp information
    - Create expert-only chunks
    - Build the hybrid retriever
    - Answer the six fixed interview-guide questions
    - Compare experts
    - Answer free-form questions across transcripts

    The LLM is loaded lazily only when a free-form question is asked.
    """

    def __init__(
        self,
        turns: list[Any],
    ) -> None:
        self.turns = turns

        # Expert-only RAG chunks.
        self.chunks = create_chunks(turns)

        if not self.chunks:
            raise ValueError(
                "No expert responses were found in the transcripts."
            )

        # Hybrid retrieval.
        self.retriever = TranscriptRetriever()
        self.retriever.build_index(self.chunks)

        # Q&A pairs used for the fixed interview guide.
        self.qa_pairs = build_qa_pairs(turns)

        # Deterministic mapping from transcript questions
        # to the six project questions.
        self.guide_mapping = map_guide_questions(
            self.qa_pairs
        )

        # Load generation model only when needed.
        self._generator: TranscriptGenerator | None = None

    @classmethod
    def from_folder(
        cls,
        data_folder: str = "data",
    ) -> "TranscriptService":
        """Load transcripts from a folder."""

        turns = parse_multiple_transcripts(
            data_folder
        )

        return cls(turns)

    @classmethod
    def from_uploaded_files(
        cls,
        uploaded_files: list[Any],
    ) -> "TranscriptService":
        """
        Build a service from uploaded Streamlit files.

        Files are temporarily written to disk so that the
        existing transcript parser can process them.
        """

        if not uploaded_files:
            raise ValueError(
                "Please upload at least one transcript."
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for uploaded_file in uploaded_files:
                file_name = Path(
                    uploaded_file.name
                ).name

                destination = (
                    temp_path / file_name
                )

                destination.write_bytes(
                    uploaded_file.getvalue()
                )

            turns = parse_multiple_transcripts(
                temp_path
            )

        return cls(turns)

    def get_experts(self) -> list[dict[str, str]]:
        """Return unique experts."""

        experts: dict[str, dict[str, str]] = {}

        for chunk in self.chunks:
            expert_name = chunk["expert"]

            if expert_name not in experts:
                experts[expert_name] = {
                    "expert": chunk["expert"],
                    "role": chunk["role"],
                    "market": chunk["market"],
                }

        return list(experts.values())

    def get_guide_questions(self) -> list[Any]:
        """Return the six fixed interview-guide questions."""

        return INTERVIEW_GUIDE

    def get_guide_answer(
        self,
        question_id: str,
        market: str,
    ) -> dict[str, Any]:
        """
        Return one fixed-guide answer for one market.

        Answers come directly from the transcript rather than
        being rewritten by the LLM.
        """

        guide_question = next(
            (
                question
                for question in INTERVIEW_GUIDE
                if question.question_id == question_id
            ),
            None,
        )

        if guide_question is None:
            raise ValueError(
                f"Unknown guide question: {question_id}"
            )

        market_data = self.guide_mapping.get(
            market
        )

        if market_data is None:
            return {
                "question_id": question_id,
                "topic": guide_question.topic,
                "question": guide_question.question,
                "market": market,
                "expert": None,
                "role": None,
                "answer": (
                    "The transcripts do not provide enough "
                    "information to answer this."
                ),
                "sources": [],
            }

        question_data = market_data.get(
            question_id
        )

        if question_data is None:
            return {
                "question_id": question_id,
                "topic": guide_question.topic,
                "question": guide_question.question,
                "market": market,
                "expert": market_data["expert"],
                "role": market_data["role"],
                "answer": (
                    "The transcripts do not provide enough "
                    "information to answer this."
                ),
                "sources": [],
            }

        sources = question_data["sources"]

        answer = " ".join(
            source["answer"]
            for source in sources
        )

        formatted_sources = []

        for source in sources:
            formatted_sources.append(
                {
                    "expert": source["expert"],
                    "role": source["role"],
                    "market": source["market"],
                    "timestamp": source["answer_timestamp"],
                    "speaker": source["speaker"],
                    "quote": source["answer"],
                    "source_file": source["source_file"],
                }
            )

        return {
            "question_id": question_id,
            "topic": guide_question.topic,
            "question": guide_question.question,
            "market": market,
            "expert": question_data["expert"],
            "role": question_data["role"],
            "answer": answer,
            "sources": formatted_sources,
        }

    def get_all_guide_answers(
        self,
    ) -> list[dict[str, Any]]:
        """Return all 18 fixed-guide answers."""

        results: list[dict[str, Any]] = []

        for question in INTERVIEW_GUIDE:
            for expert in self.get_experts():
                results.append(
                    self.get_guide_answer(
                        question_id=question.question_id,
                        market=expert["market"],
                    )
                )

        return results

    def get_comparison(self) -> dict[str, Any]:
        """Return common themes and documented differences."""

        return {
            "common_themes": identify_common_themes(
                self.guide_mapping
            ),
            "differences": identify_differences(
                self.guide_mapping
            ),
        }

    def _get_generator(self) -> TranscriptGenerator:
        """Load the LLM only when free-form Q&A is needed."""

        if self._generator is None:
            self._generator = TranscriptGenerator()

        return self._generator

    def ask(
        self,
        question: str,
        top_k: int = 6,
    ) -> dict[str, Any]:
        """
        Ask a free-form question across all transcripts.
        """

        if not question.strip():
            return {
                "question": question,
                "answer": "Please enter a question.",
                "sources": [],
            }

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

        generator = self._get_generator()

        answer = generator.generate_answer(
            question=question,
            chunks=retrieved_chunks,
        )

        sources = generator.build_sources(
            retrieved_chunks
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }