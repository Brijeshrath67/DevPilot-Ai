import os
import tempfile
from pathlib import Path

TEST_DB_PATH = Path(tempfile.gettempdir()) / "devpilot_test.db"
TEST_DATA_ROOT = Path(tempfile.gettempdir()) / "devpilot_test_data"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["DATA_ROOT"] = str(TEST_DATA_ROOT)
os.environ["AI_API_KEY"] = "mock_key"

# Keep tests hermetic and offline: blank every routed provider key so agents
# fall back to mock_key -> local rule-based logic instead of hitting live APIs.
for _provider_key in [
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "MISTRAL_API_KEY",
    "NVIDIA_API_KEY",
    "OPENROUTER_API_KEY",
    "CEREBRAS_API_KEY",
]:
    os.environ[_provider_key] = ""

for stale in [TEST_DB_PATH, TEST_DATA_ROOT]:
    if stale.exists():
        if stale.is_dir():
            import shutil

            shutil.rmtree(stale, ignore_errors=True)
        else:
            stale.unlink(missing_ok=True)

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def sample_repo_zip() -> bytes:
    import io
    import zipfile

    sample_root = Path(__file__).resolve().parents[2] / "examples" / "sample_repo"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sample_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(sample_root).as_posix())
    return buffer.getvalue()


@pytest.fixture()
def ingested_repo(client, sample_repo_zip):
    response = client.post(
        "/api/v1/repos/upload",
        files={"archive": ("sample.zip", sample_repo_zip, "application/zip")},
        data={"source_type": "archive", "repository_name": "Sample Repo"},
    )
    assert response.status_code == 200
    return response.json()["data"]["repository_id"]
