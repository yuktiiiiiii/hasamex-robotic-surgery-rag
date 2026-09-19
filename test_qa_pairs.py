from rag.parser import parse_multiple_transcripts
from rag.qa_pairs import build_qa_pairs


def main():
    turns = parse_multiple_transcripts("data")

    pairs = build_qa_pairs(turns)

    print(f"Total Q&A pairs: {len(pairs)}")

    print("\nFirst 6 pairs:\n")

    for pair in pairs[:6]:
        print("-" * 80)
        print(
            f"{pair['market']} | "
            f"{pair['expert']}"
        )

        print(
            f"Question [{pair['question_timestamp']}]: "
            f"{pair['question']}"
        )

        print(
            f"Answer [{pair['answer_timestamp']}]: "
            f"{pair['answer']}"
        )


if __name__ == "__main__":
    main()