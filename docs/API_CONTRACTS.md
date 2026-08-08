# DevPilot AI API Contracts

## Base response model

Every API response conforms to:

- `status`: `success` | `error`
- `data`: payload object or null
- `errors`: optional list of error objects
- `meta`: optional pagination or task state

## Endpoints

### POST /api/v1/repos/upload
Request body:
- `source_type`: `github_url` | `archive`
- `source_value`: URL string or file reference
- `repository_name`: optional name override

Response:
- `data.repository_id`
- `data.status`
- `data.message`

### POST /api/v1/repos/{repo_id}/analyze
Request body:
- `analysis_scope`: `structure` | `architecture` | `full`

Response:
- `data.analysis_id`
- `data.status`
- `data.summary`

### GET /api/v1/repos/{repo_id}
Response:
- `data.repository_id`
- `data.name`
- `data.status`
- `data.primary_language`
- `data.framework`
- `data.summary`
- `data.architecture_summary`

### POST /api/v1/repos/{repo_id}/code-review
Request body:
- `files`: optional list of file paths
- `review_scope`: `security` | `performance` | `maintainability` | `full`

Response:
- `data.review_id`
- `data.issues`: list of findings
- `data.recommendations`

### POST /api/v1/repos/{repo_id}/documentation
Request body:
- `doc_types`: list of `readme`, `api`, `architecture`, `install`, `contributing`, `changelog`
- `target_files`: optional list of files or modules

Response:
- `data.documents`: list of generated docs with `type`, `title`, and `content` (Markdown)

### POST /api/v1/repos/{repo_id}/documentation/pdf
Converts already-generated Markdown into a formatted PDF.

Request body:
- `title`: document title used in the PDF header and file name
- `markdown`: Markdown source to render

Response:
- `application/pdf` binary with `Content-Disposition: attachment`

### POST /api/v1/repos/{repo_id}/tests
Request body:
- `test_types`: list of `unit`, `integration`, `edge_cases`
- `target_files`: optional list of files or modules

Response:
- `data.test_id`
- `data.tests`: list of generated test cases and mock data

### POST /api/v1/repos/{repo_id}/security
Request body (optional):
- `files`: optional list of relative file paths to restrict the audit to
- `review_scope`: `full` (default) | `changes`

Response:
- `data.security_score`: 0-100, higher is safer
- `data.issues`: list of findings with `file`, `line`, `severity`, `vulnerability`, `description`, `recommendation`
- `data.recommendations`: CRITICAL/HIGH remediation lines plus audit-scope note
- `data.files_scanned`: number of files actually scanned
- `data.patterns_checked`: number of patterns in the active dictionary
- `data.scan_time_ms`: wall-clock scan duration

### POST /api/v1/repos/{repo_id}/chat
Request body:
- `question`: string
- `session_id`: optional chat session id
- `context_scope`: optional `repo_overview` | `file` | `function`

Response:
- `data.answer`
- `data.provenance`: list of source citations
- `data.session_id`

### GET /api/v1/repos/{repo_id}/files
Query params:
- none

Response:
- `data[]`: list of indexed files with `id`, `file_path`, `language`, `file_type`

### GET /api/v1/repos/{repo_id}/files/content
Query params:
- `path`: relative path of the file to read (e.g. `src/calculator.py`)

Response:
- `data.file_path`
- `data.content`: UTF-8 text content of the file

Errors:
- `404`: repository or file not found
- `400`: path escapes the repository root, or the file is binary

### GET /api/v1/repos/{repo_id}/health
Response:
- `data.documentation_score`
- `data.testing_score`
- `data.security_score`
- `data.maintainability_score`
- `data.complexity_score`
- `data.overall_score`
- `data.recommendations`

## Error model

- `errors[]`
  - `code`
  - `message`
  - `details`
