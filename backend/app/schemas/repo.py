from pydantic import BaseModel
from typing import List, Optional

class UploadRepositoryRequest(BaseModel):
    source_type: str
    source_value: Optional[str] = None
    repository_name: str | None = None

class UploadRepositoryFileRequest(BaseModel):
    repository_name: str | None = None

class AnalyzeRepositoryRequest(BaseModel):
    analysis_scope: str = "full"

class CodeReviewRequest(BaseModel):
    files: List[str] | None = None
    review_scope: str = "full"

class DocumentationRequest(BaseModel):
    doc_types: List[str]
    target_files: List[str] | None = None

class TestsRequest(BaseModel):
    test_types: List[str]
    target_files: List[str] | None = None

class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    context_scope: str | None = None
