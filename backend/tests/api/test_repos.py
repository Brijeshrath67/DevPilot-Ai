"""API-level tests for the DevPilot AI backend."""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_repositories_empty(client):
    response = client.get("/api/v1/repos")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)


def test_upload_archive_repository(client, sample_repo_zip):
    response = client.post(
        "/api/v1/repos/upload",
        files={"archive": ("sample.zip", sample_repo_zip, "application/zip")},
        data={"source_type": "archive", "repository_name": "Sample Repo"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["repository_id"] > 0
    assert data["name"] == "Sample Repo"


def test_upload_requires_valid_source_type(client):
    response = client.post(
        "/api/v1/repos/upload",
        data={"source_type": "gitlab_url", "source_value": "https://example.com/repo"},
    )
    assert response.status_code == 400


def test_upload_github_url_requires_value(client):
    response = client.post(
        "/api/v1/repos/upload",
        data={"source_type": "github_url", "source_value": ""},
    )
    assert response.status_code == 400


def test_get_repository_returns_404(client):
    response = client.get("/api/v1/repos/99999")
    assert response.status_code == 404


def test_full_repository_workflow(client, ingested_repo):
    repo_id = ingested_repo

    repo_response = client.get(f"/api/v1/repos/{repo_id}")
    assert repo_response.status_code == 200
    assert repo_response.json()["data"]["name"] == "Sample Repo"

    analyze_response = client.post(f"/api/v1/repos/{repo_id}/analyze", json={"analysis_scope": "full"})
    assert analyze_response.status_code == 200
    summary = analyze_response.json()["data"]["summary"]
    assert "files" in summary["project_summary"]
    assert "Python" in summary["languages"]

    files_response = client.get(f"/api/v1/repos/{repo_id}/files")
    assert files_response.status_code == 200
    paths = {f["file_path"] for f in files_response.json()["data"]}
    assert "src/calculator.py" in paths
    assert "README.md" in paths


def test_file_content_endpoint(client, ingested_repo):
    response = client.get(f"/api/v1/repos/{ingested_repo}/files/content", params={"path": "src/calculator.py"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["file_path"] == "src/calculator.py"
    assert "def" in payload["content"]


def test_file_content_endpoint_missing_file(client, ingested_repo):
    response = client.get(f"/api/v1/repos/{ingested_repo}/files/content", params={"path": "nope/missing.py"})
    assert response.status_code == 404


def test_file_content_endpoint_rejects_path_traversal(client, ingested_repo):
    response = client.get(f"/api/v1/repos/{ingested_repo}/files/content", params={"path": "../../etc/passwd"})
    assert response.status_code == 400


def test_file_content_endpoint_unknown_repo(client):
    response = client.get("/api/v1/repos/99999/files/content", params={"path": "README.md"})
    assert response.status_code == 404


def test_code_review_endpoint(client, ingested_repo):
    response = client.post(f"/api/v1/repos/{ingested_repo}/code-review", json={"review_scope": "full"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "issues" in payload
    assert "recommendations" in payload


def test_security_audit_endpoint_with_review_scope(client, ingested_repo):
    response = client.post(f"/api/v1/repos/{ingested_repo}/security", json={"review_scope": "full"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "issues" in payload
    assert "recommendations" in payload
    assert "files_scanned" in payload
    assert "patterns_checked" in payload


def test_documentation_endpoint(client, ingested_repo):
    response = client.post(
        f"/api/v1/repos/{ingested_repo}/documentation",
        json={"doc_types": ["readme"]},
    )
    assert response.status_code == 200
    documents = response.json()["data"]["documents"]
    assert len(documents) == 1
    assert documents[0]["type"] == "readme"
    assert documents[0]["content"]


def test_documentation_pdf_endpoint(client, ingested_repo):
    response = client.post(
        f"/api/v1/repos/{ingested_repo}/documentation/pdf",
        json={"title": "Sample Repo — README", "markdown": "# Overview\n\nHello **world**."},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert response.content.startswith(b"%PDF")


def test_documentation_pdf_endpoint_unknown_repo(client):
    response = client.post(
        "/api/v1/repos/99999/documentation/pdf",
        json={"title": "Docs", "markdown": "# Hi"},
    )
    assert response.status_code == 404


def test_tests_endpoint(client, ingested_repo):
    response = client.post(
        f"/api/v1/repos/{ingested_repo}/tests",
        json={"test_types": ["unit"]},
    )
    assert response.status_code == 200
    tests = response.json()["data"]["tests"]
    assert len(tests) == 1
    assert "pytest" in tests[0]["content"]


def test_chat_endpoint(client, ingested_repo):
    response = client.post(
        f"/api/v1/repos/{ingested_repo}/chat",
        json={"question": "What does this repository do?"},
    )
    assert response.status_code == 200
    answer = response.json()["data"]["answer"]
    assert answer


def test_health_score_endpoint(client, ingested_repo):
    response = client.get(f"/api/v1/repos/{ingested_repo}/health")
    assert response.status_code == 200
    data = response.json()["data"]
    for field in [
        "documentation_score",
        "testing_score",
        "security_score",
        "maintainability_score",
        "complexity_score",
        "overall_score",
    ]:
        assert data[field] >= 0
        assert data[field] <= 100


def test_security_audit_endpoint(client, ingested_repo):
    response = client.post(f"/api/v1/repos/{ingested_repo}/security")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["security_score"] >= 0
    assert isinstance(data["issues"], list)
    # sample repo ships an intentionally exposed secret
    assert any("secret" in issue["vulnerability"].lower() for issue in data["issues"])
