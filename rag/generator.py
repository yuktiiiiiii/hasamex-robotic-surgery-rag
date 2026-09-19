from __future__ import annotations

from typing import Any

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class TranscriptGenerator:
    """
    Generate grounded answers from retrieved transcript evidence.

    The model generates only the answer.
    Exact quotes and source metadata are taken directly
    from the retrieved transcript chunks.
    """

    def __init__(
        self,
        model_name: str = "google/flan-t5-small",
    ) -> None:
        self.model_name = model_name

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model.to(self.device)
        self.model.eval()

    def _build_context(
        self,
        chunks: list[dict[str, Any]],
    ) -> str:
        """Build evidence-only context for the LLM."""

        context_parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            context_parts.append(
                f"""Evidence {index}
Expert: {chunk["expert"]}
Role: {chunk["role"]}
Market: {chunk["market"]}
Timestamp: {chunk["timestamp"]}
Speaker: {chunk["speaker"]}
Statement: {chunk["text"]}
"""
            )

        return "\n".join(context_parts)

    def _build_prompt(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:
        """Create a strict grounded-generation prompt."""

        context = self._build_context(chunks)

        return f"""You are analyzing expert interview transcripts.

Answer the question using ONLY the evidence provided below.

Do not use outside knowledge.
Do not invent facts.
Do not invent quotes.
Do not change the meaning of the experts' statements.

If the evidence does not contain enough information to answer,
say:
"The transcripts do not provide enough information to answer this."

Question:
{question}

Evidence:
{context}

Give a concise answer based only on the evidence.
"""

    def generate_answer(
        self,
        question: str,
        chunks: list[dict[str, Any]],
        max_new_tokens: int = 150,
    ) -> str:
        """Generate a grounded answer from retrieved chunks."""

        if not chunks:
            return (
                "The transcripts do not provide enough information "
                "to answer this."
            )

        prompt = self._build_prompt(
            question=question,
            chunks=chunks,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        answer = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True,
        ).strip()

        return answer

    @staticmethod
    def build_sources(
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """
        Return exact source metadata and quotes directly
        from retrieved transcript chunks.
        """

        sources: list[dict[str, str]] = []

        for chunk in chunks:
            sources.append(
                {
                    "expert": chunk["expert"],
                    "role": chunk["role"],
                    "market": chunk["market"],
                    "timestamp": chunk["timestamp"],
                    "speaker": chunk["speaker"],
                    "quote": chunk["text"],
                    "source_file": chunk["source_file"],
                }
            )

        return sources