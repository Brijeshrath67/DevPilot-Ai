from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.repo import (
    UploadRepositoryRequest,
    AnalyzeRepositoryRequest,
    CodeReviewRequest,
    DocumentationRequest,
    TestsRequest,
    ChatRequest,
)
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService
from app.services.database_service import DatabaseService
from app.services.github_service import GitHubService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.repository_storage_service import RepositoryStorageService
from app.services.health_service import HealthService
from app.agents.orchestrator import AgentOrchestrator
from app.agents.repository_analyzer import RepositoryAnalyzerAgent
from app.agents.code_review import CodeReviewAgent
from app.agents.documentation import DocumentationAgent
from app.agents.testing import TestingAgent
from app.agents.repository_chat import RepositoryChatAgent
from app.agents.project_health import ProjectHealthAgent
from app.agents.security_agent import SecurityAgent
from app.config.settings import settings

router = APIRouter(prefix="/repos", tags=["repositories"])

llm_service = LLMService(settings.ai_api_key, settings.ai_api_url)
parser_service = ParserService()
database_service = DatabaseService()
github_service = GitHubService()
embedding_service = EmbeddingService()
vector_service = VectorService()
storage_service = RepositoryStorageService()
orchestrator = AgentOrchestrator(
    llm_service=llm_service,
    parser_service=parser_service,
    embedding_service=embedding_service,
    vector_service=vector_service,
    github_service=github_service,
    database_service=database_service,
)

orchestrator.register_agent("repository_analyzer", RepositoryAnalyzerAgent(parser_service, database_service))
orchestrator.register_agent("code_review", CodeReviewAgent(llm_service))
orchestrator.register_agent("documentation", DocumentationAgent(llm_service))
orchestrator.register_agent("testing", TestingAgent(llm_service))
orchestrator.register_agent("repository_chat", RepositoryChatAgent(llm_service, vector_service))
orchestrator.register_agent("project_health", ProjectHealthAgent(database_service))
orchestrator.register_agent("security_agent", SecurityAgent(database_service))

health_service = HealthService()

@router.post("/upload")
async def upload_repository(
    source_type: str = Form(...),
    source_value: str | None = Form(None),
    repository_name: str | None = Form(None),
    archive: UploadFile | None = File(None),
):
    if source_type not in {"github_url", "archive"}:
        raise HTTPException(status_code=400, detail="source_type must be github_url or archive")

    if source_type == "github_url":
        if not source_value:
            raise HTTPException(status_code=400, detail="source_value is required for github_url")
        repo = database_service.create_repository(
            name=repository_name or source_value,
            source_url=source_value,
            user_id=1,
        )
        try:
            extracted_path = storage_service.store_github_repository(source_value, repo.id)
            database_service.update_repository_root(int(repo.id), str(extracted_path))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to ingest GitHub repository: {exc}")

    else:
        if not archive:
            raise HTTPException(status_code=400, detail="archive file is required for archive uploads")
        repo = database_service.create_repository(
            name=repository_name or archive.filename,
            user_id=1,
        )
        try:
            extracted_path = storage_service.store_archive(archive, repo.id)
            database_service.update_repository_root(int(repo.id), str(extracted_path))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to extract repository archive: {exc}")

    return {"status": "success", "data": {"repository_id": repo.id, "name": repo.name}}

@router.post("/{repo_id}/analyze")
def analyze_repository(repo_id: str, payload: AnalyzeRepositoryRequest):
    try:
        response = orchestrator.route("repository_analyzer", {"repository_id": repo_id, "analysis_scope": payload.analysis_scope})
        return {"status": "success", "data": response}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{repo_id}")
def get_repository(repo_id: str):
    repository = database_service.get_repository(int(repo_id))
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return {
        "status": "success",
        "data": {
            "repository_id": repository.id,
            "name": repository.name,
            "source_url": repository.source_url,
            "root_path": repository.root_path,
            "status": repository.status,
            "summary": repository.summary,
            "architecture_summary": repository.architecture_summary,
        },
    }

@router.post("/{repo_id}/code-review")
def code_review_repository(repo_id: str, payload: CodeReviewRequest):
    response = orchestrator.route("code_review", {"repository_id": repo_id, "files": payload.files, "review_scope": payload.review_scope})
    return {"status": "success", "data": response}

@router.post("/{repo_id}/documentation")
def generate_documentation(repo_id: str, payload: DocumentationRequest):
    response = orchestrator.route("documentation", {"repository_id": repo_id, "doc_types": payload.doc_types, "target_files": payload.target_files})
    return {"status": "success", "data": response}

@router.post("/{repo_id}/tests")
def generate_tests(repo_id: str, payload: TestsRequest):
    response = orchestrator.route("testing", {"repository_id": repo_id, "test_types": payload.test_types, "target_files": payload.target_files})
    return {"status": "success", "data": response}

@router.post("/{repo_id}/chat")
def chat_repository(repo_id: str, payload: ChatRequest):
    response = orchestrator.route("repository_chat", {"repository_id": repo_id, "question": payload.question, "session_id": payload.session_id})
    return {"status": "success", "data": response}

@router.get("/{repo_id}/health")
def repository_health(repo_id: str):
    response = orchestrator.route("project_health", {"repository_id": repo_id})
    return {"status": "success", "data": response}

@router.post("/{repo_id}/security")
def security_audit(repo_id: str):
    response = orchestrator.route("security_agent", {"repository_id": repo_id})
    return {"status": "success", "data": response}

@router.get("/{repo_id}/status")
def get_repository_status(repo_id: str):
    repository = database_service.get_repository(int(repo_id))
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {
        "status": "success",
        "data": {
            "repository_id": repository.id,
            "status": repository.status,
        }
    }

@router.get("/{repo_id}/files")
def get_repository_files(repo_id: str):
    files = database_service.get_repository_files(int(repo_id))
    return {
        "status": "success",
        "data": [
            {
                "id": f.id,
                "file_path": f.file_path,
                "language": f.language,
                "file_type": f.file_type,
            }
            for f in files
        ]
    }
