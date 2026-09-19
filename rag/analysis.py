from __future__ import annotations

from typing import Any

from .guide import INTERVIEW_GUIDE
from .guide_mapper import map_guide_questions
from .parser import parse_multiple_transcripts
from .qa_pairs import build_qa_pairs


class InterviewGuideAnalyzer:
    """
    Analyze the six fixed interview-guide questions.

    For these predefined questions, we use the actual expert
    transcript responses as the primary answer rather than asking
    a small language model to rewrite them.

    This makes the output:
    - faithful to the source
    - easy to trace
    - resistant to hallucinated facts
    - timestamp-aware
    """

    def __init__(self, data_folder: str = "data") -> None:
        self.data_folder = data_folder

        self.turns = parse_multiple_transcripts(
            data_folder
        )

        self.qa_pairs = build_qa_pairs(
            self.turns
        )

        self.mapped = map_guide_questions(
            self.qa_pairs
        )

    def get_markets(self) -> list[str]:
        """Return all markets found in the transcripts."""
        return list(self.mapped.keys())

    @staticmethod
    def _format_direct_answer(
        sources: list[dict[str, Any]],
    ) -> str:
        """
        Build a faithful answer directly from transcript statements.

        Q4 may have two sources (training + clinical outcomes),
        while the other questions normally have one.
        """
        if not sources:
            return (
                "The transcripts do not provide enough "
                "information to answer this."
            )

        if len(sources) == 1:
            return sources[0]["answer"]

        return " ".join(
            source["answer"]
            for source in sources
        )

    @staticmethod
    def _build_sources(
        sources: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Return exact quote and timestamp information."""

        formatted_sources: list[dict[str, str]] = []

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

        return formatted_sources

    def analyze_one(
        self,
        question_id: str,
        market: str,
    ) -> dict[str, Any]:
        """
        Analyze one guide question for one market.
        """

        guide_question = next(
            (
                item
                for item in INTERVIEW_GUIDE
                if item.question_id == question_id
            ),
            None,
        )

        if guide_question is None:
            raise ValueError(
                f"Unknown guide question: {question_id}"
            )

        market_data = self.mapped.get(
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
                "expert": market_data.get("expert"),
                "role": market_data.get("role"),
                "answer": (
                    "The transcripts do not provide enough "
                    "information to answer this."
                ),
                "sources": [],
            }

        sources = question_data["sources"]

        return {
            "question_id": question_id,
            "topic": guide_question.topic,
            "question": guide_question.question,
            "market": market,
            "expert": question_data["expert"],
            "role": question_data["role"],
            "answer": self._format_direct_answer(
                sources
            ),
            "sources": self._build_sources(
                sources
            ),
        }

    def analyze_all(self) -> list[dict[str, Any]]:
        """
        Analyze all six guide questions for all experts.
        """

        results: list[dict[str, Any]] = []

        for guide_question in INTERVIEW_GUIDE:
            for market in self.get_markets():
                result = self.analyze_one(
                    question_id=guide_question.question_id,
                    market=market,
                )

                results.append(result)

        return results