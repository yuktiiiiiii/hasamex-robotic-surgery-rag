from rag.parser import parse_multiple_transcripts
from rag.qa_pairs import build_qa_pairs
from rag.guide_mapper import map_guide_questions
from rag.comparison import (
    identify_common_themes,
    identify_differences,
)


def main():
    turns = parse_multiple_transcripts("data")

    pairs = build_qa_pairs(turns)

    mapped = map_guide_questions(pairs)

    # -------------------------------------------------
    # Common themes
    # -------------------------------------------------

    common_themes = identify_common_themes(mapped)

    print("\n" + "=" * 80)
    print("COMMON THEMES")

    for item in common_themes:
        print("\n" + "-" * 60)
        print(f"Theme: {item['theme']}")
        print(
            f"Markets: "
            f"{', '.join(item['markets'])}"
        )

        print("\nEvidence:")

        # Show one piece of evidence per market.
        shown_markets = set()

        for evidence in item["evidence"]:

            if evidence["market"] in shown_markets:
                continue

            shown_markets.add(
                evidence["market"]
            )

            print(
                f"\n{evidence['market']} | "
                f"{evidence['expert']} | "
                f"{evidence['timestamp']}"
            )

            print(
                f'"{evidence["quote"]}"'
            )

    # -------------------------------------------------
    # Differences
    # -------------------------------------------------

    differences = identify_differences(mapped)

    print("\n" + "=" * 80)
    print("DOCUMENTED DIFFERENCES")

    for item in differences:
        print("\n" + "-" * 60)
        print(f"Topic: {item['topic']}")

        print("\nSummary:")
        print(item["interpretation"])

        print("\nEvidence:")

        for evidence in item["evidence"]:
            print(
                f"\n{evidence['market']} | "
                f"{evidence['expert']} | "
                f"{evidence['timestamp']}"
            )

            print(
                f'"{evidence["quote"]}"'
            )


if __name__ == "__main__":
    main()