from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .parser import TranscriptTurn


def create_chunks(turns: list[TranscriptTurn]) -> list[dict[str, Any]]:
    """
    Create RAG chunks from expert responses only.

    Interviewer questions are excluded because the application
    should retrieve evidence from expert answers.
    """
    chunks: list[dict[str, Any]] = []

    for turn in turns:
        # Ignore interviewer questions.
        if turn.speaker.strip().lower() == "interviewer":
            continue

        chunk = asdict(turn)

        chunk["chunk_index"] = len(chunks)

        # Text used for embedding and retrieval.
        chunk["retrieval_text"] = (
            f"Expert: {turn.expert}\n"
            f"Role: {turn.role}\n"
            f"Market: {turn.market}\n"
            f"Timestamp: {turn.timestamp}\n"
            f"Speaker: {turn.speaker}\n"
            f"Statement: {turn.text}"
        )

        chunks.append(chunk)

    return chunks