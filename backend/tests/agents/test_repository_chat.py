"""Tests for the Repository Chat agent."""

from unittest.mock import MagicMock

from app.agents.repository_chat import RepositoryChatAgent


def test_missing_question_returns_error():
    agent = RepositoryChatAgent(MagicMock())
    assert agent.handle({}) == {"error": "Missing message"}


def test_answers_question_with_provenance():
    rag = MagicMock()
    rag.answer.return_value = ("grounded answer", ["src/app.py", "README.md"], "grounded")
    agent = RepositoryChatAgent(rag)

    result = agent.handle({"repository_id": "1", "question": "What does app.py do?"})

    assert result == {
        "answer": "grounded answer",
        "provenance": ["src/app.py", "README.md"],
        "mode": "grounded",
    }
    rag.answer.assert_called_once_with("What does app.py do?", top_k=5)


def test_accepts_message_alias_and_top_k():
    rag = MagicMock()
    rag.answer.return_value = ("answer", [], "open")
    agent = RepositoryChatAgent(rag)

    result = agent.handle({"message": "Explain the architecture", "top_k": 3})

    assert result["answer"] == "answer"
    assert result["mode"] == "open"
    rag.answer.assert_called_once_with("Explain the architecture", top_k=3)


def test_message_takes_precedence_over_question():
    rag = MagicMock()
    rag.answer.return_value = ("answer", [], "open")
    agent = RepositoryChatAgent(rag)

    agent.handle({"message": "used", "question": "ignored"})

    rag.answer.assert_called_once_with("used", top_k=5)
