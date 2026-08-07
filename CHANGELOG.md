# Changelog

All notable changes to the **DevPilot AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-08

### Added
- Backend pytest suite covering the full API workflow, agents, security skill, parser, and vector store.
- Frontend linting (eslint + typescript-eslint), typecheck, and vitest unit tests.
- Playwright end-to-end suite covering ingest, code review, project health, and security scan.
- GitHub Actions pipelines: `backend.yml`, `frontend.yml`, `test.yml`, and `deploy.yml`.
- Docker images and Compose file (`docker/`) for backend and frontend.
- Developer scripts: `setup`, `run`, `seed`, `cleanup` (`.sh` + `.ps1`) and the portable `make_sample_zip.py` fixture builder.
- Pre-commit hooks (lint, formatting, secrets, tests, build).
- `docs/TESTING.md` guide and expanded `README.md`.

### Fixed
- Security scanner now detects `aws_secret_access_key`, f-string SQL interpolation, and list-form `pyproject.toml` dependencies.
- E2E selector strict-mode violations resolved.

## [0.1.0] - 2026-08-07

### Added
- Created custom `SecuritySkill` for static vulnerability scans.
- Created custom `SecurityAgent` for automated security grading.
- Implemented `/repos/{repo_id}/security`, `/repos/{repo_id}/status`, and `/repos/{repo_id}/files` FastAPI endpoints.
- Implemented pure-Python cosine-similarity vector store with local JSON persistence for offline RAG support.
- Refactored `ProjectHealthAgent` to calculate dynamic scores based on README existence, testing files, and repository size.
- Implemented Pydantic V2 compatibility changes in settings classes.
- Added comprehensive developer dashboard with multi-page navigation layout (Dashboard, Review, Docs, Tests, QA Chat, Health, Settings).
