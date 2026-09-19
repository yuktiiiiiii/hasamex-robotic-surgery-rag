from rag.chat import TranscriptChat


def main():
    print("Loading transcript chat...")

    chat = TranscriptChat()

    question = (
        "What do the experts say about surgeon training?"
    )

    print("\nQuestion:")
    print(question)

    result = chat.ask(
        question,
        top_k=6,
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(result["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in result["sources"]:
        print(
            f"\n{source['market']} | "
            f"{source['expert']} | "
            f"{source['timestamp']}"
        )

        print(
            f'{source["speaker"]}: '
            f'"{source["quote"]}"'
        )


if __name__ == "__main__":
    main()