from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)


class RAGSkill:
    """Retrieval-augmented generation with an open chat fallback.

    When repository context is retrieved the answer is grounded in it and
    cites file paths. When nothing matches, the assistant still answers from
    general knowledge instead of refusing — the response reports ``mode``
    so callers can tell ``grounded`` from ``open`` answers.
    """

    def __init__(self, vector_service: Any, embedding_service: Any, llm: Any = None) -> None:
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.llm = llm

    def retrieve_context(self, query: str, top_k: int = 5) -> list[Any]:
        return self.vector_service.query_vectors(query, top_k=top_k)

    def _source(self, entry: dict[str, Any]) -> str:
        metadata = entry.get("metadata") or {}
        return metadata.get("file_path") or entry.get("id") or "unknown"

    def _build_grounded_prompt(self, question: str, context: list[Any]) -> str:
        snippets = []
        for entry in context:
            source = self._source(entry)
            text = entry.get("text", "")[:600]
            if text:
                snippets.append(f"[{source}]\n{text}")
        context_block = "\n\n".join(snippets)
        return (
            "You are DevPilot, an expert software engineering assistant.\n\n"
            "The user asked a question about a repository. Use the retrieved repository "
            "context below as your primary reference.\n\n"
            f"CONTEXT:\n{context_block}\n\n"
            "Answer the question thoroughly. Cite the relevant file paths from the "
            "context when you use them. You may also draw on your general knowledge to "
            "complete or explain the answer, but keep it accurate and directly relevant "
            "to the question.\n\n"
            f"QUESTION: {question}"
        )

    def _build_open_prompt(self, question: str) -> str:
        return (
            "You are DevPilot, an expert software engineering assistant. The user asked "
            "a question in a repository workspace, but no matching repository context "
            "was retrieved for it.\n\n"
            "Answer the question openly and helpfully using your knowledge. If the "
            "question is about this specific repository and you cannot be certain, say "
            "so and suggest what to check in the codebase.\n\n"
            f"QUESTION: {question}"
        )

    def build_prompt(self, question: str, context: list[Any]) -> str:
        if not context:
            return self._build_open_prompt(question)
        return self._build_grounded_prompt(question, context)

    def _fallback_answer(self, question: str, context: list[Any]) -> str:
        if context:
            lines = []
            for entry in context:
                source = self._source(entry)
                text = entry.get("text", "").strip()
                if text:
                    lines.append(f"[{source}] {text[:300]}")
            return (
                "I could not reach the AI provider, so here is the closest retrieved "
                "repository context for your question:\n\n" + "\n\n".join(lines)
            )
        return (
            f"The AI provider is not configured, so I can't generate a full answer for "
            f"“{question}”. Check the provider keys in the backend configuration and try "
            "again, or ask about something in the analyzed repository."
        )

    def answer(self, question: str, top_k: int = 5) -> tuple[str, list[str], str]:
        context = self.retrieve_context(question, top_k=top_k)
        mode = "grounded" if context else "open"
        answer = ""
        if self.llm is not None:
            prompt = self.build_prompt(question, context)
            answer = self.llm.generate(prompt, temperature=0.4, max_tokens=1024)
            if answer.startswith("LLM request failed"):
                logger.warning("Chat LLM unavailable; falling back to local response.")
                answer = self._fallback_answer(question, context)
        else:
            answer = self._fallback_answer(question, context)
        provenance = [self._source(entry) for entry in context]
        return answer, provenance, mode
