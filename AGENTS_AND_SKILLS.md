# DevPilot AI — Custom Agents & Skills

This document details the custom agents and skills implemented within DevPilot
AI. Every agent and skill is committed to the repository, unit-tested, and wired
into the live application.

---

## 1. Custom Skills

### 1.1 Security Scanner Skill (`SecuritySkill`)

- **File Path**: `backend/app/skills/security_skill.py`
- **Purpose**: Provides static code analysis scans across repository files to
  locate potential vulnerability patterns and credential disclosures.
- **Capabilities**:
  - **Secret Scans**: regex-based detection of exposed API keys, JWT secrets,
    Bearer tokens, and AWS credential parameters.
  - **Unsafe Method Audits**: scans for `eval()`, `exec()`, `os.system()` and
    other raw-string execution risks.
  - **SQL Injection Risks**: detects non-parameterized database executions
    (string concatenation, `%`-modulation, f-string interpolation).
- **Tests**: `backend/tests/agents/test_security_skill.py`

### 1.2 RAG Skill (`RAGSkill`)

- **File Path**: `backend/app/skills/rag_skill.py`
- **Purpose**: Retrieval-augmented generation. Retrieves repository context from
  the vector store, builds a grounded prompt with file-path citations, and
  answers through the routed LLM (default: OpenRouter). Answers carry a
  `provenance` list for source tracing.

### 1.3 Reporting Skill (`ReportingSkill`)

- **File Path**: `backend/app/skills/reporting_skill.py`
- **Purpose**: Computes the five health sub-scores plus the overall health score
  from raw metrics, and formats structured summaries for agents and the UI.

---

## 2. Custom Agents

DevPilot AI ships **seven** agents. Six are AI agents, each bound to a **distinct
LLM provider** via the provider registry (`backend/app/core/providers.py`); the
seventh is a pure rule-based security auditor.

### 2.1 Repository Analyzer Agent → Groq

- **File Path**: `backend/app/agents/repository_analyzer.py`
- **Purpose**: Analyzes repository structure, detects languages/frameworks/
  dependencies, indexes files into storage, and persists project + architecture
  summaries.
- **LLM Integration**: when a real Groq key is configured, the agent asks Groq
  for a richer project summary; otherwise it falls back to rule-based parsing.

### 2.2 Code Review Agent → Hugging Face

- **File Path**: `backend/app/agents/code_review.py`
- **Purpose**: Runs a static security scan (via `SecuritySkill`) and, when a
  real Hugging Face key is configured, a qualitative LLM review pass. Returns
  severity-graded `issues` and actionable `recommendations`.

### 2.3 Documentation Agent → Mistral

- **File Path**: `backend/app/agents/documentation.py`
- **Purpose**: Generates README, API, architecture, install, contributing, and
  changelog documents. Uses Mistral via `DocumentationService`, with built-in
  template fallback when the key is a `mock_key`.

### 2.4 Testing Agent → NVIDIA

- **File Path**: `backend/app/agents/testing.py`
- **Purpose**: Generates unit/integration/e2e test scaffolds (pytest) using the
  NVIDIA NIM API via `TestingService`, with deterministic template fallback.

### 2.5 Repository Chat Agent → OpenRouter

- **File Path**: `backend/app/agents/repository_chat.py`
- **Purpose**: Contextual QA over the repository. Uses `RAGSkill` to retrieve
  context from the vector store and answer through OpenRouter, returning
  `answer` + `provenance` citations.

### 2.6 Project Health Agent → Cerebras

- **File Path**: `backend/app/agents/project_health.py`
- **Purpose**: Computes documentation/testing/security/maintainability/complexity
  scores plus an overall score, persists them, and returns recommendations. When
  a real Cerebras key is configured, the LLM supplements rule-based
  recommendations with concrete improvement bullets.

### 2.7 Security Audit Agent (rule-based, custom)

- **File Path**: `backend/app/agents/security_agent.py`
- **Purpose**: Consumes `SecuritySkill` to execute full-repository security
  compliance audits.
- **Capabilities**:
  - **Dynamic Security Scoring**: starts at 100 and subtracts penalties for
    critical/high/medium findings.
  - **Health Metric Propagation**: persists computed scores into the project's
    centralized health metrics.
  - **Actionable Remediation Alerts**: returns severity-categorized findings with
    file, line, and remediation steps.
- **Tests**: `backend/tests/agents/test_agents.py`

---

## 3. Provider Routing

| Agent | Provider | Base URL |
| --- | --- | --- |
| Repository Analyzer | Groq | `https://api.groq.com/openai/v1` |
| Code Review | Hugging Face | `https://router.huggingface.co/v1` |
| Documentation | Mistral | `https://api.mistral.ai/v1` |
| Testing | NVIDIA | `https://integrate.api.nvidia.com/v1` |
| Repository Chat | OpenRouter | `https://openrouter.ai/api/v1` |
| Project Health | Cerebras | `https://api.cerebras.ai/v1` |

Routing is centralized in `backend/app/core/providers.py` (the
`LLMProviderRegistry`) and driven by `settings.agent_llm_providers`. Any missing
provider key falls back to `AI_API_KEY`, keeping the app fully functional
offline with `mock_key`.
