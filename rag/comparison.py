from __future__ import annotations

from collections import defaultdict
from typing import Any


THEME_RULES: dict[str, list[str]] = {
    "Cost / Budget / Economics": [
        "cost",
        "capital budget",
        "capital purchases",
        "hospital finances",
        "economic case",
        "economics",
        "roi",
        "pay for itself",
        "financial",
        "funding",
        "maintenance",
        "service contracts",
        "total cost of ownership",
    ],
    "Training / Workforce": [
        "training",
        "trained",
        "surgeon",
        "surgeons",
        "theatre staff",
        "staff",
        "comfortable using it",
    ],
    "Procedure Volume / Utilisation": [
        "utilisation",
        "procedure volume",
        "used enough",
        "volume",
        "sustainable",
    ],
    "Clinical Outcomes": [
        "clinical outcomes",
        "patient outcomes",
        "length of stay",
        "clinical case",
        "clinical strategy",
    ],
    "Uneven Hospital Access / Adoption": [
        "uneven",
        "smaller hospitals",
        "regional hospitals",
        "larger academic hospitals",
        "university hospitals",
        "access still varies",
        "larger nhs trusts",
        "private centres",
    ],
    "Gradual Growth": [
        "steadily",
        "gradual",
        "not expect a dramatic jump",
        "high single digits",
        "low double digits",
        "continue increasing",
    ],
}


def _contains_theme(text: str, keywords: list[str]) -> bool:
    """Return True when any theme keyword occurs in text."""

    text_lower = text.lower()

    return any(
        keyword.lower() in text_lower
        for keyword in keywords
    )


def identify_common_themes(
    mapped: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Identify themes that appear in expert evidence
    from at least two different markets.
    """

    theme_markets: dict[str, set[str]] = defaultdict(set)
    theme_evidence: dict[str, list[dict[str, str]]] = defaultdict(list)

    for market, question_data in mapped.items():

        for _, question_info in question_data.items():

            for source in question_info["sources"]:

                text = source["answer"]

                for theme, keywords in THEME_RULES.items():

                    if not _contains_theme(
                        text,
                        keywords,
                    ):
                        continue

                    theme_markets[theme].add(market)

                    theme_evidence[theme].append(
                        {
                            "market": source["market"],
                            "expert": source["expert"],
                            "timestamp": source[
                                "answer_timestamp"
                            ],
                            "quote": source["answer"],
                        }
                    )

    common_themes: list[dict[str, Any]] = []

    for theme, markets in theme_markets.items():

        if len(markets) < 2:
            continue

        common_themes.append(
            {
                "theme": theme,
                "markets": sorted(markets),
                "evidence": theme_evidence[theme],
            }
        )

    return common_themes


def identify_differences(
    mapped: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Capture documented differences in emphasis across experts.

    This does not declare a winner. It reports what each expert
    emphasized in the transcript.
    """

    differences: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # Economics emphasis
    # ---------------------------------------------------------

    economic_evidence: list[dict[str, str]] = []

    for market, questions in mapped.items():

        q3 = questions.get("Q3")

        if not q3:
            continue

        for source in q3["sources"]:
            economic_evidence.append(
                {
                    "market": market,
                    "expert": source["expert"],
                    "timestamp": source[
                        "answer_timestamp"
                    ],
                    "quote": source["answer"],
                }
            )

    differences.append(
        {
            "topic": "Role of economics in purchasing",
            "evidence": economic_evidence,
            "interpretation": (
                "The experts place different emphasis on economics. "
                "The France and Germany responses describe strong "
                "economic or financial approval requirements, while "
                "the UK response describes economics as balanced with "
                "clinical strategy."
            ),
        }
    )

    # ---------------------------------------------------------
    # Growth outlook
    # ---------------------------------------------------------

    growth_evidence: list[dict[str, str]] = []

    for market, questions in mapped.items():

        q5 = questions.get("Q5")

        if not q5:
            continue

        for source in q5["sources"]:
            growth_evidence.append(
                {
                    "market": market,
                    "expert": source["expert"],
                    "timestamp": source[
                        "answer_timestamp"
                    ],
                    "quote": source["answer"],
                }
            )

    differences.append(
        {
            "topic": "Expected adoption growth",
            "evidence": growth_evidence,
            "interpretation": (
                "The experts all describe continued growth, but "
                "their quantitative expectations differ. France "
                "mentions 15–20 percent more procedures annually in "
                "some stronger centres, Germany describes high "
                "single-digit or low double-digit growth for the "
                "market, and the UK mentions growth above 15 percent "
                "annually in some areas."
            ),
        }
    )

    # ---------------------------------------------------------
    # Purchase timeline
    # ---------------------------------------------------------

    timeline_evidence: list[dict[str, str]] = []

    for market, questions in mapped.items():

        q6 = questions.get("Q6")

        if not q6:
            continue

        for source in q6["sources"]:
            timeline_evidence.append(
                {
                    "market": market,
                    "expert": source["expert"],
                    "timestamp": source[
                        "answer_timestamp"
                    ],
                    "quote": source["answer"],
                }
            )

    differences.append(
        {
            "topic": "Purchase timeline",
            "evidence": timeline_evidence,
            "interpretation": (
                "The stated timelines differ across markets. "
                "France gives six to twelve months, Germany gives "
                "nine to eighteen months, and the UK gives around "
                "six to nine months when funding is already available, "
                "with longer waits possible when a new capital cycle "
                "is required."
            ),
        }
    )

    return differences