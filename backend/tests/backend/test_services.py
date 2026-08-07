"""Unit tests for the parser and vector services."""

from pathlib import Path

from app.services.parser_service import ParserService
from app.services.vector_service import VectorService


class TestParserService:
    def test_detect_languages_and_frameworks(self, tmp_path: Path):
        (tmp_path / "package.json").write_text(
            '{"dependencies": {"react": "^18.0.0", "axios": "^1.0.0"}}',
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("fastapi>=0.110.0\npytest>=8.0.0\n", encoding="utf-8")
        (tmp_path / "app.py").write_text("print('hi')\n", encoding="utf-8")
        (tmp_path / "index.tsx").write_text("export const a = 1;\n", encoding="utf-8")

        parsed = ParserService()._parse_repository(tmp_path)

        assert "Python" in parsed["languages"]
        assert "TypeScript" in parsed["languages"]
        assert "FastAPI" in parsed["frameworks"]
        assert "react" in parsed["dependencies"]
        assert "pytest" in parsed["dependencies"]

    def test_summarize_project_builds_sentence(self):
        parser = ParserService()
        parsed = {
            "file_count": 12,
            "languages": ["Python", "TypeScript"],
            "frameworks": ["FastAPI"],
            "dependencies": ["pydantic", "httpx"],
        }
        summary = parser._summarize_project("MyApp", parsed)
        assert "MyApp contains 12 source files" in summary
        assert "2 dependencies" in summary

    def test_parse_pyproject_toml(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[project]\ndependencies = [\n  'fastapi',\n  'uvicorn',\n]\n",
            encoding="utf-8",
        )
        parsed = ParserService()._parse_repository(tmp_path)
        assert "fastapi" in parsed["dependencies"]
        assert "FastAPI" in parsed["frameworks"]


class TestVectorService:
    def test_upsert_and_query(self, tmp_path):
        service = VectorService(index_path=tmp_path / "index.json")
        items = [
            {
                "id": "f1",
                "vector": [0.0],
                "text": "The FastAPI app exposes a health endpoint.",
                "metadata": {"repository_id": "1", "file_path": "main.py"},
            }
        ]
        service.upsert_vectors(items)

        hits = service.query_vectors("fastapi health endpoint", top_k=1)
        assert hits, "expected at least one match"
        assert hits[0]["id"] == "f1"
        assert hits[0]["metadata"]["repository_id"] == "1"

    def test_query_with_empty_index_returns_empty(self, tmp_path):
        service = VectorService(index_path=tmp_path / "empty.json")
        assert service.query_vectors("anything") == []

    def test_upsert_deduplicates(self, tmp_path):
        service = VectorService(index_path=tmp_path / "index.json")
        item = {"id": "a", "vector": [0.0], "text": "text", "metadata": {}}
        service.upsert_vectors([item])
        service.upsert_vectors([item])
        assert len(service.data) == 1
