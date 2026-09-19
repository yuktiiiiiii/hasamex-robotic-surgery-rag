from rag.parser import parse_multiple_transcripts
from rag.qa_pairs import build_qa_pairs
from rag.guide_mapper import map_guide_questions


def main():
    turns = parse_multiple_transcripts("data")
    pairs = build_qa_pairs(turns)

    mapped = map_guide_questions(pairs)

    for market, questions in mapped.items():
        print("\n" + "=" * 80)
        print(market)

        for question_id, data in questions.items():
            print("\n" + "-" * 60)
            print(question_id)
            print(f"Expert: {data['expert']}")

            for source in data["sources"]:
                print(
                    f"[{source['answer_timestamp']}] "
                    f"{source['speaker']}: "
                    f"{source['answer']}"
                )


if __name__ == "__main__":
    main()