"""Test scaffolding service built on an LLM generator with deterministic fallback."""

from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)

TEMPLATES = {
    "unit": """import pytest

def test_addition():
    assert add(2, 3) == 5

def test_subtraction():
    assert subtract(5, 3) == 2
""",
    "integration": """import pytest
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
""",
    "e2e": """import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_full_workflow(client):
    response = client.get("/api/v1/repos")
    assert response.status_code == 200
""",
}


class TestingService:
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    def generate(self, test_types: list[str], target_files: list[str] | None = None) -> list[dict[str, str]]:
        tests = []
        for test_type in test_types:
            target = ""
            if target_files:
                target = f" targeting files: {', '.join(target_files[:10])}"
            prompt = f"Create {test_type} tests for the repository{target}."
            content = self._generate(prompt, test_type)
            tests.append({"type": test_type, "content": content})
        return tests

    def _generate(self, prompt: str, test_type: str) -> str:
        try:
            if hasattr(self.llm, "generate_text"):
                content = self.llm.generate_text(prompt)
            else:
                content = self.llm.generate(prompt)
            if content and not content.startswith("LLM request failed"):
                return content
        except Exception as exc:  # noqa: BLE001  # graceful fallback per constitution
            logger.warning("Test generation via LLM failed (%s); using template", exc)
        return TEMPLATES.get(test_type, TEMPLATES["unit"])
