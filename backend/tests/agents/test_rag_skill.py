"""Tests for the RAG skill's open chat behavior."""

from unittest.mock import MagicMock

from app.skills.rag_skill import RAGSkill


def test_answer_grounded_when_context_exists():
    vector = MagicMock()
    vector.query_vectors.return_value = [
        {"id": "1", "text": "def add(a, b): return a + b", "metadata": {"file_path": "src/math.py"}}
    ]
    llm = MagicMock()
    llm.generate.return_value = "It uses math.py to add numbers."
    skill = RAGSkill(vector, MagicMock(), llm)

    _answer, provenance, mode = skill.answer("How is addition done?")

    assert mode == "grounded"
    assert provenance == ["src/math.py"]
    prompt = llm.generate.call_args[0][0]
    assert "src/math.py" in prompt
    assert "You may also draw on your general knowledge" in prompt


def test_answer_open_when_no_context():
    vector = MagicMock()
    vector.query_vectors.return_value = []
    llm = MagicMock()
    llm.generate.return_value = "Here is a general explanation of how HTTP works."
    skill = RAGSkill(vector, MagicMock(), llm)

    _answer, provenance, mode = skill.answer("Explain HTTP status codes")

    assert mode == "open"
    assert provenance == []
    prompt = llm.generate.call_args[0][0]
    assert "Answer the question openly and helpfully" in prompt


def test_fallback_when_llm_unavailable_and_no_context():
    vector = MagicMock()
    vector.query_vectors.return_value = []
    skill = RAGSkill(vector, MagicMock(), llm=None)

    answer, provenance, mode = skill.answer("Explain async vs sync")

    assert mode == "open"
    assert provenance == []
    assert "AI provider is not configured" in answer


def test_llm_failure_falls_back_to_context():
    vector = MagicMock()
    vector.query_vectors.return_value = [{"id": "1", "text": "Flask app entry", "metadata": {"file_path": "app.py"}}]
    llm = MagicMock()
    llm.generate.return_value = "LLM request failed (timeout). Falling back to local rules."
    skill = RAGSkill(vector, MagicMock(), llm)

    answer, _, mode = skill.answer("What is the entry point?")

    assert mode == "grounded"
    assert "app.py" in answer
