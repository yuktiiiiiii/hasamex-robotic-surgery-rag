from rag.analyzer import TranscriptAnalyzer


def main():
    analyzer = TranscriptAnalyzer()

    print(
        f"Loaded transcript turns: "
        f"{len(analyzer.turns)}"
    )

    print(
        f"Expert chunks: "
        f"{len(analyzer.chunks)}"
    )

    print("\nExperts:")

    for expert in analyzer.get_experts():
        print(
            f"- {expert['expert']} | "
            f"{expert['market']}"
        )

    print("\nRunning interview-guide analysis...")

    results = analyzer.analyze_interview_guide()

    for result in results:
        print("\n" + "=" * 80)
        print(
            f"{result['question_id']} | "
            f"{result['topic']}"
        )
        print(result["question"])

        for expert in result["experts"]:
            print("\n" + "-" * 80)
            print(
                f"{expert['market']} | "
                f"{expert['expert']}"
            )

            print("\nAnswer:")
            print(expert["answer"])

            print("\nSources:")

            for source in expert["sources"]:
                print(
                    f"{source['timestamp']} | "
                    f"{source['speaker']}"
                )
                print(
                    f'"{source["quote"]}"'
                )


if __name__ == "__main__":
    main()