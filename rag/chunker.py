from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .parser import TranscriptTurn


def create_chunks(turns: list[TranscriptTurn]) -> list[dict[str, Any]]:
    """
    Convert parsed transcript turns into RAG-ready chunks.

    Each timestamped speaker turn becomes one chunk.
    We preserve the original transcript text and all source metadata
    so answers can always be traced back to the transcript.
    """
    chunks: list[dict[str, Any]] = []

    for index, turn in enumerate(turns):
        chunk = asdict(turn)

        chunk["chunk_index"] = index

        # Text used for embedding/retrieval.
        # Including metadata helps retrieval distinguish experts/markets.
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