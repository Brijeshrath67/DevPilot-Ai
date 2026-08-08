from app.agents.base_agent import BaseAgent
from app.skills.rag_skill import RAGSkill


class RepositoryChatAgent(BaseAgent):
    """Answers questions about the repository — grounded when context exists,
    open (general knowledge) when it does not."""

    def __init__(self, rag_skill: RAGSkill) -> None:
        self.rag_skill = rag_skill

    def handle(self, payload: dict) -> dict:
        question = payload.get("message") or payload.get("question")
        if not question:
            return {"error": "Missing message"}
        answer, provenance, mode = self.rag_skill.answer(question, top_k=payload.get("top_k", 5))
        return {"answer": answer, "provenance": provenance, "mode": mode}
