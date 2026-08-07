from pydantic import BaseModel


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
