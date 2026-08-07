# DevPilot AI Testing Guide

This document describes how to run and extend the DevPilot AI test suites.

## Test layout

| Layer | Tooling | Location |
| --- | --- | --- |
| Backend unit/integration | pytest | `backend/tests/` |
| Frontend unit | vitest + React Testing Library | `frontend/src/**/*.test.{ts,tsx}` |
| End-to-end | Playwright | `frontend/tests/e2e/` |

## Backend tests

```bash
cd backend
pytest -q tests
```

Coverage areas:

- `tests/api/test_repos.py` — upload → analyze → review → docs → tests → chat → health → security workflow over the live FastAPI app.
- `tests/agents/test_agents.py` — agent payload handling, health score ranges, security grading.
- `tests/agents/test_security_skill.py` — vulnerability detection rules (SQL injection, hardcoded secrets, `os.system`, etc.).
- `tests/backend/test_services.py` — parser, vector store, and skill orchestration.

Linting and format checks:

```bash
ruff check app tests
ruff format --check app tests
```

## Frontend unit tests

```bash
cd frontend
npm run test        # vitest run (CI mode)
npm run test:watch  # interactive watch
```

## End-to-end tests

Playwright drives the real stack. `frontend/playwright.config.ts` starts the
FastAPI backend and the Vite dev server automatically via `webServer`, so no
servers need to be running beforehand.

```bash
cd frontend
npx playwright test           # run all
npx playwright test --ui      # interactive UI
npx playwright show-report    # view the HTML report
```

The e2e suite (`tests/e2e/dashboard.spec.ts`) exercises the complete product
flow against a deterministic fixture built by `scripts/make_sample_zip.py`:

1. **Ingest** — uploads `examples/sample_repo` and runs the full analysis.
2. **Code Review** — runs a review and asserts severity-graded findings appear.
3. **Project Health** — computes and displays health scorecards.
4. **Security Scan** — surfaces remediation items.

Each run writes artifacts under `frontend/test-results/` and
`frontend/playwright-report/` (both gitignored).

## CI

The same suites run in GitHub Actions:

- `backend.yml` — ruff + pytest.
- `frontend.yml` — eslint + typecheck + vitest + `npm run build`.
- `test.yml` — Playwright with browser install, HTML report, and failure traces.

## Adding a new test

1. Backend: add `backend/tests/<area>/test_<thing>.py` following existing fixtures in `backend/tests/conftest.py`.
2. Frontend unit: co-locate `<Component>.test.tsx` beside the component.
3. E2E: add a `test(...)` in `tests/e2e/dashboard.spec.ts` reusing `ingestSampleRepository`.
4. Run the full suite locally before pushing — the workflows mirror these commands exactly.
