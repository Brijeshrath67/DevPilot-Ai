import api from "../lib/api";
import type {
  ApiEnvelope,
  AnalyzeResult,
  ChatResult,
  CodeReviewResult,
  DocumentationResult,
  HealthResult,
  Repository,
  RepositoryDetail,
  RepositoryFile,
  RepositoryFileContent,
  SecurityResult,
  TestsResult,
  UploadResult,
} from "../types/api";

export function getRepositories(): Promise<ApiEnvelope<Repository[]>> {
  return api.get("/repos").then((r) => r.data);
}

export function uploadRepository(payload: {
  sourceType: "github_url" | "archive";
  sourceValue?: string;
  repositoryName?: string;
  archive?: File;
}): Promise<ApiEnvelope<UploadResult>> {
  const form = new FormData();
  form.append("source_type", payload.sourceType);
  if (payload.sourceValue) form.append("source_value", payload.sourceValue);
  if (payload.repositoryName) form.append("repository_name", payload.repositoryName);
  if (payload.archive) form.append("archive", payload.archive);
  return api
    .post("/repos/upload", form, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data);
}

export function getRepository(repoId: number | string): Promise<ApiEnvelope<RepositoryDetail>> {
  return api.get(`/repos/${repoId}`).then((r) => r.data);
}

export function getRepositoryFiles(repoId: number | string): Promise<ApiEnvelope<RepositoryFile[]>> {
  return api.get(`/repos/${repoId}/files`).then((r) => r.data);
}

export function getRepositoryFileContent(
  repoId: number | string,
  path: string
): Promise<ApiEnvelope<RepositoryFileContent>> {
  return api.get(`/repos/${repoId}/files/content`, { params: { path } }).then((r) => r.data);
}

export function getRepositoryStatus(repoId: number | string): Promise<ApiEnvelope<{ repository_id: number; status: string }>> {
  return api.get(`/repos/${repoId}/status`).then((r) => r.data);
}

export function analyzeRepository(
  repoId: number | string,
  analysisScope = "full"
): Promise<ApiEnvelope<AnalyzeResult>> {
  return api.post(`/repos/${repoId}/analyze`, { analysis_scope: analysisScope }).then((r) => r.data);
}

export function runCodeReview(
  repoId: number | string,
  reviewScope = "full",
  files?: string[]
): Promise<ApiEnvelope<CodeReviewResult>> {
  return api.post(`/repos/${repoId}/code-review`, { review_scope: reviewScope, files }).then((r) => r.data);
}

export function runSecurityAudit(repoId: number | string): Promise<ApiEnvelope<SecurityResult>> {
  return api.post(`/repos/${repoId}/security`).then((r) => r.data);
}

export function generateDocumentation(
  repoId: number | string,
  docTypes: string[],
  targetFiles?: string[]
): Promise<ApiEnvelope<DocumentationResult>> {
  return api
    .post(`/repos/${repoId}/documentation`, { doc_types: docTypes, target_files: targetFiles })
    .then((r) => r.data);
}

export async function exportDocumentationPdf(
  repoId: number | string,
  title: string,
  markdown: string
): Promise<Blob> {
  const response = await api.post(`/repos/${repoId}/documentation/pdf`, { title, markdown }, {
    responseType: "blob",
  });
  return response.data as Blob;
}

export function generateTests(
  repoId: number | string,
  testTypes: string[],
  targetFiles?: string[]
): Promise<ApiEnvelope<TestsResult>> {
  return api.post(`/repos/${repoId}/tests`, { test_types: testTypes, target_files: targetFiles }).then((r) => r.data);
}

export function chatWithRepository(
  repoId: number | string,
  question: string,
  sessionId?: string
): Promise<ApiEnvelope<ChatResult>> {
  return api.post(`/repos/${repoId}/chat`, { question, session_id: sessionId }).then((r) => r.data);
}

export function getProjectHealth(repoId: number | string): Promise<ApiEnvelope<HealthResult>> {
  return api.get(`/repos/${repoId}/health`).then((r) => r.data);
}
