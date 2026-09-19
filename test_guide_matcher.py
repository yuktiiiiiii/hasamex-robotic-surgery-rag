from rag.parser import parse_multiple_transcripts
from rag.qa_pairs import build_qa_pairs
from rag.guide_matcher import find_guide_evidence


def main():
    turns = parse_multiple_transcripts("data")
    pairs = build_qa_pairs(turns)

    markets = [
        "France",
        "Germany",
        "United Kingdom",
    ]

    questions = [
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5",
        "Q6",
    ]

    for question_id in questions:
        print("\n" + "=" * 80)
        print(question_id)

        for market in markets:
            print("\n" + "-" * 60)
            print(market)

            evidence = find_guide_evidence(
                pairs=pairs,
                question_id=question_id,
                market=market,
                max_results=3,
            )

            for item in evidence:
                print(
                    f"\nScore: {item['evidence_score']}"
                )
                print(
                    f"Question "
                    f"[{item['question_timestamp']}]: "
                    f"{item['question']}"
                )
                print(
                    f"Answer "
                    f"[{item['answer_timestamp']}]: "
                    f"{item['answer']}"
                )


if __name__ == "__main__":
    main()