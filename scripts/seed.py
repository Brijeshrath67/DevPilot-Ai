#!/usr/bin/env python3
"""Seed the DevPilot AI database with the bundled sample repository.

Run standalone (no server required):

    python scripts/seed.py

It creates a Repository record pointing at examples/sample_repo, indexes its
files in the database and vector store, and runs the repository analysis agent
so the UI has data to display.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.agents.repository_analyzer import RepositoryAnalyzerAgent
from app.config.settings import settings
from app.db import init_db
from app.models.repository import Repository
from app.services.database_service import DatabaseService
from app.services.parser_service import ParserService


def main() -> None:
    init_db()
    db_service = DatabaseService()

    sample_dir = ROOT / "examples" / "sample_repo"
    if not sample_dir.is_dir():
        print("examples/sample_repo not found; build the fixture first.")
        print("  python scripts/make_sample_zip.py")
        return

    from app.db.session import SessionLocal

    with SessionLocal() as session:
        repo = (
            session.query(Repository)
            .filter(Repository.name == "E2E Sample Repo")
            .first()
        )
    if repo is not None:
        print(f"==> E2E Sample Repo already exists (id={repo.id}), re-analyzing")
    else:
        print("==> Creating E2E Sample Repo repository record")
        repo = db_service.create_repository(
            name="E2E Sample Repo", root_path=str(sample_dir)
        )

    db_service.update_repository_root(repo.id, str(sample_dir))

    print("==> Running repository analysis agent (parsing, vector indexing, summary)")
    agent = RepositoryAnalyzerAgent(ParserService(), db_service)
    agent.handle({"repository_id": str(repo.id), "analysis_scope": "full"})

    print(f"==> Done. Open http://localhost:5173/repo/{repo.id} to view the results.")
    print(f"    (LLM calls use API key: {settings.ai_api_key!r})")


if __name__ == "__main__":
    main()
