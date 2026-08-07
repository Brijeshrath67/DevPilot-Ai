from typing import Any


class RAGSkill:
    """Retrieval-augmented generation: retrieve context, then answer via LLM."""

    def __init__(self, vector_service: Any, embedding_service: Any, llm: Any = None) -> None:
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.llm = llm

    def retrieve_context(self, query: str, top_k: int = 5) -> list[Any]:
        return self.vector_service.query_vectors(query, top_k=top_k)

    def build_prompt(self, question: str, context: list[Any]) -> str:
        if not context:
            return (
                f"No repository context was found for: {question}. "
                "Run analysis and index the repository before asking questions."
            )
        snippets = []
        for entry in context:
            source = entry.get("metadata", {}).get("file_path", entry.get("id", "unknown"))
            text = entry.get("text", "")[:400]
            snippets.append(f"[{source}]\n{text}")
        context_block = "\n\n".join(snippets)
        return (
            f"Answer the question strictly using the retrieved repository context below.\n\n"
            f"CONTEXT:\n{context_block}\n\nQUESTION: {question}\n\n"
            "Cite file paths from the context in your answer. If the context lacks "
            "the answer, say so explicitly."
        )

    def answer(self, question: str, top_k: int = 5) -> tuple[str, list[Any]]:
        context = self.retrieve_context(question, top_k=top_k)
        prompt = self.build_prompt(question, context)
        if self.llm is not None:
            answer = self.llm.generate(prompt, temperature=0.1, max_tokens=512)
        else:
            answer = prompt
        provenance = [entry.get("text", "") for entry in context if entry.get("text")]
        return answer, provenance
