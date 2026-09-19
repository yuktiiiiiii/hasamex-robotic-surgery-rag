from __future__ import annotations

from dataclasses import asdict, dataclass

from .parser import TranscriptTurn


@dataclass
class ExpertQAPair:
    """One interviewer question paired with the expert's response."""

    expert: str
    role: str
    market: str

    question_timestamp: str
    question: str

    answer_timestamp: str
    speaker: str
    answer: str

    source_file: str


def build_qa_pairs(
    turns: list[TranscriptTurn],
) -> list[dict]:
    """
    Pair each interviewer question with the following expert answer.

    This is important because the six interview-guide questions
    correspond directly to specific interviewer questions in each
    transcript.
    """

    pairs: list[dict] = []

    for index, turn in enumerate(turns):
        # We only start a pair when we find an interviewer question.
        if turn.speaker.strip().lower() != "interviewer":
            continue

        # The next turn should be the expert's response.
        if index + 1 >= len(turns):
            continue

        next_turn = turns[index + 1]

        # Safety checks.
        if next_turn.speaker.strip().lower() == "interviewer":
            continue

        if next_turn.market != turn.market:
            continue

        pair = ExpertQAPair(
            expert=next_turn.expert,
            role=next_turn.role,
            market=next_turn.market,
            question_timestamp=turn.timestamp,
            question=turn.text,
            answer_timestamp=next_turn.timestamp,
            speaker=next_turn.speaker,
            answer=next_turn.text,
            source_file=next_turn.source_file,
        )

        pairs.append(asdict(pair))

    return pairs