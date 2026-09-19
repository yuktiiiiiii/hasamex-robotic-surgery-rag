from rag.analysis import InterviewGuideAnalyzer


def main():
    analyzer = InterviewGuideAnalyzer()

    results = analyzer.analyze_all()

    print(
        f"Total guide answers: {len(results)}"
    )

    for result in results:
        print("\n" + "=" * 80)

        print(
            f"{result['question_id']} | "
            f"{result['topic']}"
        )

        print(
            f"{result['market']} | "
            f"{result['expert']}"
        )

        print("\nQuestion:")
        print(result["question"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:
            print(
                f"[{source['timestamp']}] "
                f"{source['speaker']}"
            )

            print(
                f'"{source["quote"]}"'
            )


if __name__ == "__main__":
    main()