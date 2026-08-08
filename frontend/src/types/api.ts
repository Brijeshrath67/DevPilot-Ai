export type RepoStatus = "pending" | "analyzing" | "analyzed" | "error";

export interface ApiEnvelope<T> {
  status: "success" | "error";
  data: T;
}

export interface Repository {
  repository_id: number;
  name: string;
  source_url: string | null;
  status: string;
  summary: string | null;
  created_at: string | null;
}

export interface RepositoryDetail {
  repository_id: number;
  name: string;
  source_url: string | null;
  root_path: string | null;
  status: string;
  summary: string | null;
  architecture_summary: string | null;
}

export interface RepositoryFile {
  id: number;
  file_path: string;
  language: string | null;
  file_type: string | null;
}

export interface RepositoryFileContent {
  file_path: string;
  content: string;
}

export interface AnalysisSummary {
  project_summary: string;
  architecture_summary: string;
  languages: string[];
  frameworks: string[];
  dependencies: string[];
}

export interface AnalyzeResult {
  repository_id: number;
  summary: AnalysisSummary;
}

export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "MINOR";

export interface Finding {
  severity: Severity;
  file: string;
  line: number;
  vulnerability: string;
  description: string;
  recommendation: string;
}

export interface CodeReviewResult {
  security_score: number;
  issues: Finding[];
  recommendations: string[];
}

export interface SecurityResult {
  security_score: number;
  issues: Finding[];
  recommendations: string[];
  files_scanned: number;
  patterns_checked: number;
  scan_time_ms: number;
}

export interface GeneratedDocument {
  type: string;
  title?: string;
  content: string;
}

export interface DocumentationResult {
  documents: GeneratedDocument[];
}

export interface GeneratedTest {
  type: string;
  content: string;
}

export interface TestsResult {
  tests: GeneratedTest[];
}

export interface ChatResult {
  answer: string;
  provenance: string[];
  mode?: "grounded" | "open";
}

export interface HealthResult {
  documentation_score: number;
  testing_score: number;
  security_score: number;
  maintainability_score: number;
  complexity_score: number;
  overall_score: number;
  recommendations: string[];
}

export interface UploadResult {
  repository_id: number;
  name: string;
}
