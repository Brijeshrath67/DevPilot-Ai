from pydantic import BaseModel


class UploadRepositoryRequest(BaseModel):
    source_type: str
    source_value: str | None = None
    repository_name: str | None = None


class UploadRepositoryFileRequest(BaseModel):
    repository_name: str | None = None


class AnalyzeRepositoryRequest(BaseModel):
    analysis_scope: str = "full"


class CodeReviewRequest(BaseModel):
    files: list[str] | None = None
    review_scope: str = "full"


class DocumentationRequest(BaseModel):
    doc_types: list[str]
    target_files: list[str] | None = None


class TestsRequest(BaseModel):
    test_types: list[str]
    target_files: list[str] | None = None


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    context_scope: str | None = None
