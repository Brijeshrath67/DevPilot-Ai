# DevPilot AI — Product Requirements Document (PRD)

> Status: **Implemented** — this PRD describes the current, shipping state of the
> project and the requirements the system must satisfy going forward.

## 1. What We Are Building

**DevPilot AI** is an AI-powered developer productivity platform. A user uploads
a repository (ZIP archive or GitHub URL) and DevPilot analyzes it end to end:
it summarizes structure and dependencies, grades code quality, scans for
security vulnerabilities, writes documentation, scaffolds tests, answers
questions about the codebase, and scores project health — all from one web
dashboard.

The system is built as a **two-tier web application**:

- **Backend** — Python `FastAPI` service exposing a REST API (`/api/v1/repos/*`),
  driven by a pipeline of specialized AI agents. Each agent owns one workflow and
  is backed by a distinct LLM provider (Groq, Hugging Face, NVIDIA, OpenRouter),
  with deterministic rule-based fallbacks so the entire platform works **offline
  with zero API keys**.
- **Frontend** — React (`Vite` + `TypeScript` + `Tailwind CSS`) single-page app
  with dedicated pages for every workflow: Dashboard, Repository Overview, Code
  Review, Security, Documentation (with PDF export), Testing, QA Chat, Project
  Health, and Settings.

The whole stack is deployable with Docker Compose, fully tested (unit,
integration, and Playwright end-to-end), and buildable end to end with a single
script (`scripts/build.sh` / `scripts/build.ps1`).

## 2. Who It Is For

| Persona | What they need |
|---|---|
| **Developer** | Fast, grounded answers about a codebase; docs and test scaffolds; obvious security warnings before they merge. |
| **Tech Lead / Code Reviewer** | Severity-graded findings with file/line provenance, health trends across five dimensions, and ready-to-run test scaffolds before approving changes. |
| **Maintainer / Evaluator** | A demonstrable end-to-end flow, clean architecture, green CI/CD, and a system that works offline without paid API keys. |

## 3. System-Wide Principles (Constitution)

Every feature inherits these requirements:

1. **Security first** — never log or commit secrets; `.env` files are
   git-ignored; findings always carry file/line provenance.
2. **Explainability** — AI answers cite the source files they come from; scores
   are deterministic and recomputable.
3. **Graceful failure** — LLM timeouts and unreachable external stores fall back
   to local rule-based logic; users never see raw crash output.
4. **Accuracy over hallucination** — chat answers are grounded in retrieved
   context and explicitly say when context is missing instead of guessing.

## 4. Functional Requirements

### FR1 — Repository Ingestion
**User story**: "As a developer, I want to upload my repository as a ZIP or from
a GitHub URL so I can start analysis immediately."

**Acceptance criteria**:
- `POST /api/v1/repos/upload` accepts `source_type=archive` (multipart) or
  `source_type=github_url`.
- A repository record is created with a unique id and `status` transitions
  `created → ingested`.
- Invalid source types and missing archives return `400`.

### FR2 — Repository Analysis
**User story**: "As a developer, I want the platform to summarize my repository's
structure, languages, frameworks, and dependencies."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/analyze` returns `project_summary`,
  `architecture_summary`, `languages`, `frameworks`, `dependencies`.
- The file index is persisted and `GET /api/v1/repos/{repo_id}/files` lists
  files with language and file type.
- The Repository Analyzer Agent uses **Groq** when a real key is present,
  otherwise rule-based parsing still produces a complete summary.

### FR3 — Code Review
**User story**: "As a tech lead, I want severity-graded code review findings with
fix recommendations."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/code-review` returns `issues` (severity, file,
  line, vulnerability, description, recommendation) and `recommendations`.
- Static security scanning always runs; the Code Review Agent (**Hugging Face**)
  adds a qualitative LLM pass when a real key is present.
- The sample repository's intentionally exposed secret is always detected.

### FR4 — Security Audit
**User story**: "As a maintainer, I want a dedicated, rule-based security scan."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/security` returns `security_score`, `issues`,
  `recommendations`, `files_scanned`, `patterns_checked`, and `scan_time_ms`.
- The Security Agent is fully rule-based (no LLM) using the security skill's
  pattern dictionary (secrets, path traversal, unsafe functions, injection).
- `review_scope=changes` limits the audit to files changed since HEAD on a git
  checkout.
- The endpoint reports a 100.0 score when no repository or no issues exist.

### FR5 — Documentation Generation
**User story**: "As a developer, I want to generate README, API, architecture,
install, contributing, and changelog documents."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/documentation` with `doc_types` returns one
  `{type, content}` document per requested type.
- Supported types: `readme`, `api`, `architecture`, `install`, `contributing`,
  `changelog`.
- Output is valid Markdown; deterministic templates are used when the **Groq**
  key is unavailable. Generation runs in parallel (up to 4 workers).

### FR6 — Documentation PDF Export
**User story**: "As a developer, I want to export generated documentation as a
PDF so I can share it."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/documentation/pdf` accepts a title and Markdown
  and returns a valid PDF file.
- Rendering uses `reportlab` and never fails the request when markdown contains
  arbitrary or malformed content.

### FR7 — Test Generation
**User story**: "As a developer, I want pytest unit/integration/e2e scaffolds for
my repository."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/tests` with `test_types` returns one `{type,
  content}` scaffold per type.
- Supported types: `unit`, `integration`, `e2e`.
- Generated content is executable pytest; **NVIDIA NIM** powers generation when a
  real key is present, with template fallback otherwise.

### FR8 — Repository QA Chat
**User story**: "As a developer, I want to ask questions about my codebase and
get answers that cite the relevant files."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/chat` returns `answer` and `provenance`.
- Answers are grounded in retrieved vector context (Pinecone or local index) and
  generated through **OpenRouter**.
- The RAG skill reports a `mode` (`grounded` vs `open`): when no context matches
  it answers from general knowledge but labels the response, so callers never
  confuse an open answer for a grounded one.

### FR9 — Project Health Dashboard
**User story**: "As a tech lead, I want a health scorecard covering documentation,
testing, security, maintainability, and complexity."

**Acceptance criteria**:
- `GET /api/v1/repos/{repo_id}/health` returns five sub-scores, an
  `overall_score`, and `recommendations`.
- Scores are persisted and deterministic; the Project Health Agent uses
  **OpenRouter** to supplement recommendations when a real key is present.

### FR10 — Multi-Provider LLM Routing
**User story**: "As an operator, I want each agent to use a specific LLM provider
and fall back gracefully when a key is missing."

**Acceptance criteria**:
- Six agents map to providers via `settings.agent_llm_providers`:
  `repository_analyzer → groq`, `code_review → huggingface`,
  `documentation → groq`, `testing → nvidia`,
  `repository_chat → openrouter`, `project_health → openrouter`.
- Missing provider keys fall back to `AI_API_KEY` (default `mock_key`).
- All workflows remain fully functional offline with a single mock key.

### FR11 — Storage Flexibility
**User story**: "As an operator, I want the data stack to run on MongoDB Atlas +
Pinecone in production and degrade to SQLite + a local index locally."

**Acceptance criteria**:
- `MONGODB_URI` enables the Atlas backend; otherwise SQLite is used.
- `VECTOR_STORE=pinecone` + `PINECONE_API_KEY` enables Pinecone; otherwise a
  local JSON index is used.
- No endpoint breaks when external stores are unreachable.

### FR12 — Frontend Dashboard
**User story**: "As a user, I want one dashboard that guides me through every
workflow."

**Acceptance criteria**:
- Pages exist for: Dashboard (workspace list), Repository Overview (analyze +
  file index), Code Review, Security, Documentation (generate + PDF download),
  Testing, QA Chat, Project Health, and Settings.
- Workspace creation supports both ZIP upload (multipart) and GitHub URL with a
  source-type toggle.
- Every workflow page shows results inline with progress/loading states and a
  clear path to re-run the analysis.

### FR13 — Unified Build & Run
**User story**: "As an operator, I want to build, test, seed, and start the whole
stack with one command."

**Acceptance criteria**:
- `scripts/build.sh` (and `scripts/build.ps1` on Windows) executes the full
  pipeline: prerequisites → setup (venv, pip, npm) → build (backend imports +
  frontend `tsc`/`vite build`) → lint/format/typecheck → pytest + vitest →
  Playwright e2e → seed sample repo → start backend + frontend.
- Granular flags (`--setup`, `--build`, `--check`, `--test`, `--e2e`, `--seed`,
  `--run`, `--skip-e2e`, `--no-run`) allow running individual phases.

### FR14 — CI/CD Pipeline
**User story**: "As a maintainer, I want every push validated automatically."

**Acceptance criteria**:
- GitHub Actions workflows cover: backend (ruff + 123 pytest tests), frontend
  (eslint, typecheck, vitest, production build), and Playwright E2E with an HTML
  report artifact.
- The E2E workflow can be triggered manually (`workflow_dispatch`) and runs the
  full user journey (create workspace → analyze → review → security → docs →
  tests → chat → health).
- Docker Compose deployment for production.

## 5. Non-Functional Requirements

- **Performance** — documentation generation runs in parallel; security scans
  report `scan_time_ms`; the full E2E suite completes in ~1 minute on CI.
- **Reliability** — every external dependency (LLM, MongoDB, Pinecone) degrades
  gracefully; the platform is fully usable offline.
- **Testability** — 123 backend tests, 5 frontend tests, and 4 Playwright
  end-to-end scenarios all pass in CI.
- **Security** — secrets never logged or committed; `.env` git-ignored;
  path-traversal and unsafe-function patterns detected by the security skill.
- **Maintainability** — `ruff` clean, `eslint` + `tsc` clean, docs in `docs/`
  (architecture, API contracts, this PRD, release plan, roadmap).

## 6. Out of Scope (Current MVP)

- Multi-user auth flows beyond JWT scaffolding (GitHub OAuth optional).
- Real-time streaming responses.
- Fine-grained per-file review selection UI (API supports `files`/`scope`
  already; full UI surfacing is future work).
- Non-pytest test framework generation.

## 7. Definition of Done

- Working code committed with tests, lint-clean, and a green CI run.
- Architecture doc, agent rules, PRD, and task breakdown present in `docs/`.
- At least one custom agent and one custom skill documented in
  `AGENTS_AND_SKILLS.md`.
- Playwright e2e report uploaded as a CI artifact.
- The entire stack builds and runs from a single command
  (`./scripts/build.sh`).
- Semver tag / release created.
