from __future__ import annotations

from collections import defaultdict
from typing import Any


# Transcript order mapped to the project's six guide questions.
#
# Each expert transcript has 7 Q&A pairs:
#
# 0 -> Q1 Current adoption
# 1 -> Q2 Barriers
# 2 -> Q3 Budget / ROI
# 3 -> Q4 Training
# 4 -> Q4 Clinical outcomes
# 5 -> Q5 Adoption trend
# 6 -> Q6 Purchase timeline
#
# Q4 combines transcript pairs 3 and 4.


def map_guide_questions(
    pairs: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Map transcript Q&A pairs to the six project guide questions.

    Returns:

    {
        "France": {
            "Q1": {
                "expert": ...,
                "sources": [...]
            },
            ...
        },
        ...
    }
    """

    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for pair in pairs:
        by_market[pair["market"]].append(pair)

    results: dict[str, dict[str, dict[str, Any]]] = {}

    for market, market_pairs in by_market.items():

        # Keep transcript order.
        # The transcripts are already parsed in chronological order.
        if len(market_pairs) < 7:
            raise ValueError(
                f"{market} has only {len(market_pairs)} Q&A pairs. "
                "Expected at least 7."
            )

        results[market] = {
            "Q1": {
                "expert": market_pairs[0]["expert"],
                "role": market_pairs[0]["role"],
                "market": market,
                "sources": [market_pairs[0]],
            },
            "Q2": {
                "expert": market_pairs[1]["expert"],
                "role": market_pairs[1]["role"],
                "market": market,
                "sources": [market_pairs[1]],
            },
            "Q3": {
                "expert": market_pairs[2]["expert"],
                "role": market_pairs[2]["role"],
                "market": market,
                "sources": [market_pairs[2]],
            },
            "Q4": {
                "expert": market_pairs[3]["expert"],
                "role": market_pairs[3]["role"],
                "market": market,
                "sources": [
                    market_pairs[3],
                    market_pairs[4],
                ],
            },
            "Q5": {
                "expert": market_pairs[5]["expert"],
                "role": market_pairs[5]["role"],
                "market": market,
                "sources": [market_pairs[5]],
            },
            "Q6": {
                "expert": market_pairs[6]["expert"],
                "role": market_pairs[6]["role"],
                "market": market,
                "sources": [market_pairs[6]],
            },
        }

    return results