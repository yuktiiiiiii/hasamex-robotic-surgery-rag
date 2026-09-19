from rag.parser import parse_multiple_transcripts
from rag.chunks import create_chunks
from rag.retriever import TranscriptRetriever


def main():
    # 1. Read all transcripts
    turns = parse_multiple_transcripts("data")

    # 2. Convert turns into RAG chunks
    chunks = create_chunks(turns)

    print(f"Total chunks: {len(chunks)}")

    # 3. Build hybrid retriever
    retriever = TranscriptRetriever()
    retriever.build_index(chunks)

    # 4. Test query
    query = "What are the main barriers to adoption?"

    # 5. Search only within France for this test
    results = retriever.search(
        query,
        top_k=3,
        market="France",
    )

    print("\nTop results:\n")

    for result in results:
        print("-" * 80)
        print(f"Market: {result['market']}")
        print(f"Expert: {result['expert']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Speaker: {result['speaker']}")
        print(
            f"Retrieval Score: "
            f"{result['retrieval_score']:.4f}"
        )
        print(f"Text: {result['text']}")


if __name__ == "__main__":
    main()