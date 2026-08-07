# DevPilot AI — Product Requirements Document

## 1. Overview

DevPilot AI is a workflow-centric developer productivity platform. Users upload
a repository (ZIP or GitHub URL), and the platform analyzes it, reviews its
code, generates documentation and tests, answers questions about the codebase,
and reports project health — all driven by six specialized AI agents, each
backed by a distinct LLM provider.

## 2. Goals

- Give developers a single dashboard for repository analysis, review, docs,
  tests, QA chat, and health monitoring.
- Make every AI workflow explainable: answers cite files, findings carry
  severity, and scores are deterministic.
- Ship a production-shaped, fully offline-capable MVP: every provider and data
  store degrades gracefully when credentials are missing.

## 3. Personas

- **Developer** — wants fast, grounded answers about a codebase and actionable
  review/health feedback.
- **Tech Lead / Reviewer** — wants severity-graded findings, docs, test scaffolds,
  and health trends before approving changes.
- **Evaluator / Maintainer** — wants a demonstrable end-to-end flow with clean
  architecture and CI/CD.

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
- `POST /api/v1/repos/{repo_id}/analyze` returns a summary with
  `project_summary`, `architecture_summary`, `languages`, `frameworks`,
  `dependencies`.
- File index is persisted and `GET /api/v1/repos/{repo_id}/files` lists files
  with language and file type.
- The Repository Analyzer Agent uses **Groq** when a real key is present,
  otherwise rule-based parsing still produces a summary.

### FR3 — Code Review
**User story**: "As a tech lead, I want severity-graded code review findings with
fix recommendations."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/code-review` returns `issues` (severity, file,
  line, vulnerability, description, recommendation) and `recommendations`.
- Static security scanning always runs; the Code Review Agent (Hugging Face) adds a
  qualitative LLM pass when a real key is present.
- The sample repo's intentionally exposed secret is always detected.

### FR4 — Documentation Generation
**User story**: "As a developer, I want to generate README, API, architecture,
install, and changelog documents."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/documentation` with `doc_types` returns one
  `{type, content}` document per requested type.
- Output is valid Markdown; deterministic templates are used when the Mistral
  key is unavailable.

### FR5 — Test Generation
**User story**: "As a developer, I want pytest unit/integration/e2e scaffolds for
my repository."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/tests` with `test_types` returns one `{type,
  content}` scaffold per type.
- Generated content is executable pytest; NVIDIA NIM powers generation when a
  real key is present, with template fallback otherwise.

### FR6 — Repository QA Chat
**User story**: "As a developer, I want to ask questions about my codebase and
get answers that cite the relevant files."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/chat` returns `answer` and `provenance`.
- Answers are grounded in retrieved vector context (Pinecone or local index)
  and generated through OpenRouter.
- When no context exists, the agent says so explicitly instead of guessing.

### FR7 — Project Health Dashboard
**User story**: "As a tech lead, I want a health scorecard covering
documentation, testing, security, maintainability, and complexity."

**Acceptance criteria**:
- `GET /api/v1/repos/{repo_id}/health` returns five sub-scores, an
  `overall_score`, and `recommendations`.
- Scores are persisted and deterministic; Project Health Agent uses **Cerebras**
  to supplement recommendations when a real key is present.

### FR8 — Security Audit
**User story**: "As a maintainer, I want a dedicated security scan endpoint."

**Acceptance criteria**:
- `POST /api/v1/repos/{repo_id}/security` returns `security_score`, `issues`,
  and `recommendations`.
- Findings are severity-graded; the endpoint reports a 100.0 score when no
  repository or no issues exist.

### FR9 — Multi-Provider LLM Routing
**User story**: "As an operator, I want each agent to use a specific LLM provider
and fall back gracefully when a key is missing."

**Acceptance criteria**:
- Six agents map to six providers (Groq, Hugging Face, Mistral, NVIDIA, OpenRouter,
  Cerebras) via `settings.agent_llm_providers`.
- Missing provider keys fall back to `AI_API_KEY` (default `mock_key`).
- All workflows remain fully functional offline with a single mock key.

### FR10 — Storage Flexibility
**User story**: "As an operator, I want the data stack to run on MongoDB Atlas +
Pinecone in production and degrade to SQLite + a local index locally."

**Acceptance criteria**:
- `MONGODB_URI` enables the Atlas backend; otherwise SQLite is used.
- `VECTOR_STORE=pinecone` + `PINECONE_API_KEY` enables Pinecone; otherwise a
  local JSON index is used.
- No endpoint breaks when external stores are unreachable.

## 5. Non-Functional Requirements

- **Security first**: secrets never logged or committed; `.env` files are
  git-ignored.
- **Explainability**: findings carry `file`/`line` provenance; RAG answers return
  `provenance`.
- **Graceful failure**: LLM timeouts and unavailable stores fall back to local
  rule-based logic — never raw crash output to users.
- **Accuracy over hallucination**: chat refuses to fabricate answers when
  context is missing.
- **CI/CD green**: backend lint+tests, frontend lint/typecheck/build/tests, and
  Playwright e2e (with HTML report artifact) all run in GitHub Actions.

## 6. Out of Scope (MVP)

- Multi-user auth flows beyond JWT scaffolding (GitHub OAuth optional).
- Real-time streaming responses.
- Fine-grained per-file review selection UI.

## 7. Definition of Done

- Working code committed with tests, lint-clean, and a green CI run.
- Architecture doc, agent rules, PRD, and task breakdown present in the repo.
- At least one custom agent and one custom skill documented in
  `AGENTS_AND_SKILLS.md`.
- Playwright e2e report uploaded as a CI artifact.
- Semver tag / release created.
