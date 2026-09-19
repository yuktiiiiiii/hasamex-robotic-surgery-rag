from __future__ import annotations

import re
from typing import Any


GUIDE_KEYWORDS: dict[str, list[str]] = {
    "Q1": [
        "adoption",
        "adoption today",
        "current adoption",
        "describe adoption",
        "market",
    ],
    "Q2": [
        "barrier",
        "barriers",
        "holding back",
        "obstacle",
        "funding",
        "cost",
        "adoption",
    ],
    "Q3": [
        "budget",
        "roi",
        "economic",
        "economics",
        "financial",
        "capital",
        "cost",
        "pay for itself",
    ],
    "Q4": [
        "training",
        "trained",
        "surgeon",
        "surgeons",
        "clinical",
        "outcomes",
        "patient outcomes",
    ],
    "Q5": [
        "expect",
        "future",
        "three",
        "five",
        "years",
        "growth",
        "increase",
        "accelerate",
        "trend",
    ],
    "Q6": [
        "purchase",
        "purchasing",
        "decision",
        "timeline",
        "how long",
        "capital cycle",
        "months",
    ],
}


def normalize(text: str) -> str:
    """Normalize text for lightweight keyword matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def score_pair(
    pair: dict[str, Any],
    keywords: list[str],
) -> int:
    """
    Score a Q&A pair against guide-specific keywords.

    We score both the interviewer question and the expert answer,
    but give more importance to the interviewer question because
    it tells us what the expert was asked.
    """
    question = normalize(pair["question"])
    answer = normalize(pair["answer"])

    score = 0

    for keyword in keywords:
        keyword = normalize(keyword)

        if not keyword:
            continue

        # Stronger signal when the keyword occurs in the
        # interviewer question.
        if keyword in question:
            score += 3

        # Additional supporting signal from the answer.
        if keyword in answer:
            score += 1

    return score


def find_guide_evidence(
    pairs: list[dict[str, Any]],
    question_id: str,
    market: str,
    max_results: int = 3,
) -> list[dict[str, Any]]:
    """
    Find transcript Q&A pairs relevant to one interview-guide
    question for a specific market.

    Only existing transcript evidence is returned.
    Nothing is generated here.
    """
    if question_id not in GUIDE_KEYWORDS:
        raise ValueError(
            f"Unknown guide question: {question_id}"
        )

    market_pairs = [
        pair
        for pair in pairs
        if pair["market"].strip().lower()
        == market.strip().lower()
    ]

    keywords = GUIDE_KEYWORDS[question_id]

    scored_pairs: list[tuple[int, dict[str, Any]]] = []

    for pair in market_pairs:
        score = score_pair(pair, keywords)

        if score > 0:
            scored_pairs.append(
                (score, pair)
            )

    scored_pairs.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        {
            **pair,
            "evidence_score": score,
        }
        for score, pair in scored_pairs[:max_results]
    ]