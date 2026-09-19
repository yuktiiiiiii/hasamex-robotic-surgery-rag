from rag.service import TranscriptService


def main():
    service = TranscriptService.from_folder("data")

    print(f"Experts: {len(service.get_experts())}")
    print(f"Chunks: {len(service.chunks)}")
    print(
        f"Guide answers: "
        f"{len(service.get_all_guide_answers())}"
    )

    comparison = service.get_comparison()

    print(
        f"Common themes: "
        f"{len(comparison['common_themes'])}"
    )

    print(
        f"Differences: "
        f"{len(comparison['differences'])}"
    )


if __name__ == "__main__":
    main()