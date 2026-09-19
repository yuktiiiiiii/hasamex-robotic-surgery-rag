from rag.parser import parse_multiple_transcripts
from rag.chunks import create_chunks
from rag.retriever import TranscriptRetriever
from rag.generator import TranscriptGenerator


def main():
    # -------------------------------------------------
    # 1. Load transcripts
    # -------------------------------------------------
    turns = parse_multiple_transcripts("data")
    print(f"Parsed transcript turns: {len(turns)}")

    # -------------------------------------------------
    # 2. Create expert-only chunks
    # -------------------------------------------------
    chunks = create_chunks(turns)
    print(f"Expert chunks: {len(chunks)}")

    # -------------------------------------------------
    # 3. Build hybrid retriever
    # -------------------------------------------------
    print("\nBuilding retriever...")
    retriever = TranscriptRetriever()
    retriever.build_index(chunks)

    # -------------------------------------------------
    # 4. Ask one interview-guide question
    # -------------------------------------------------
    question = "What are the main barriers to adoption?"

    print(f"\nQuestion:\n{question}")

    retrieved_chunks = retriever.search(
        question,
        top_k=5,
    )

    print("\nRetrieved evidence:")
    print("=" * 80)

    for chunk in retrieved_chunks:
        print(
            f"\n{chunk['market']} | "
            f"{chunk['expert']} | "
            f"{chunk['timestamp']}"
        )
        print(f"Speaker: {chunk['speaker']}")
        print(f"Text: {chunk['text']}")
        print(
            f"Retrieval score: "
            f"{chunk['retrieval_score']:.4f}"
        )

    # -------------------------------------------------
    # 5. Generate grounded answer
    # -------------------------------------------------
    print("\nLoading answer generator...")

    generator = TranscriptGenerator()

    answer = generator.generate_answer(
        question=question,
        chunks=retrieved_chunks,
    )

    # -------------------------------------------------
    # 6. Display answer
    # -------------------------------------------------
    print("\nGenerated Answer:")
    print("=" * 80)
    print(answer)

    # -------------------------------------------------
    # 7. Display exact sources
    # -------------------------------------------------
    sources = generator.build_sources(
        retrieved_chunks
    )

    print("\nSources:")
    print("=" * 80)

    for source in sources:
        print(
            f"\n{source['market']} — "
            f"{source['expert']} — "
            f"{source['timestamp']}"
        )
        print(f"Speaker: {source['speaker']}")
        print(f'Quote: "{source["quote"]}"')
        print(f"File: {source['source_file']}")


if __name__ == "__main__":
    main()