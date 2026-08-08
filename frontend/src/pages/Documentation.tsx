import { useState } from "react";
import { useParams } from "react-router-dom";
import { BookOpen } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { RunPanel } from "../components/features/RunPanel";
import { AnalyzeGate } from "../components/features/AnalyzeGate";
import { GeneratedDocPanel } from "../components/features/GeneratedDocPanel";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Card } from "../components/ui/Card";
import { Checkbox } from "../components/ui/Checkbox";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useDocumentation } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";
import { titleCase } from "../lib/utils";
import type { DocumentationResult } from "../types/api";

const DOC_TYPES = ["readme", "api", "architecture", "install", "contributing", "changelog"];

export function DocumentationPage() {
  const { repoId } = useParams();
  const { error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const docs = useDocumentation(repoId);

  const [selected, setSelected] = useState<string[]>(["readme"]);
  const [result, setResult] = useState<DocumentationResult | null>(null);

  const repo = repoQuery.data?.data;
  const loading = repoQuery.isLoading || statusLoading;

  const toggle = (docType: string) => {
    setSelected((prev) =>
      prev.includes(docType) ? prev.filter((d) => d !== docType) : [...prev, docType]
    );
  };

  const run = () => {
    docs.mutate(
      { docTypes: selected },
      {
        onSuccess: (res) => setResult(res.data),
        onError: (err) => toastError(err instanceof Error ? err.message : "Documentation generation failed."),
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Documentation"
        description="Generate project documentation — README, API reference, architecture, installation, contributing, and changelog."
        icon={<BookOpen className="h-5 w-5" />}
        badge={repo ? <RepoStatusBadge status={status ?? repo.status} /> : undefined}
      />

      {loading ? (
        <Card className="p-5">
          <SkeletonLines lines={4} />
        </Card>
      ) : !repo ? (
        <Card className="p-4">
          <p className="py-10 text-center text-sm text-ink-3">Repository not found.</p>
        </Card>
      ) : isProcessing(status) ? (
        <Card className="p-5">
          <p className="py-8 text-center text-sm text-ink-3">Workspace is still being analyzed — wait for analysis to finish.</p>
        </Card>
      ) : status !== "analyzed" ? (
        <AnalyzeGate repoId={repoId!} />
      ) : (
        <>
          <RunPanel
            icon={<BookOpen className="h-4 w-4" />}
            title="Documentation targets"
            description="Select the document types to generate. Multiple selections are supported."
            onRun={run}
            isRunning={docs.isPending}
            disabled={selected.length === 0}
            runLabel={result ? "Re-generate" : "Generate documentation"}
            options={
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {DOC_TYPES.map((docType) => (
                  <Checkbox
                    key={docType}
                    label={titleCase(docType).replace("_", " ")}
                    checked={selected.includes(docType)}
                    onChange={() => toggle(docType)}
                  />
                ))}
              </div>
            }
          />

          {docs.isPending && (
            <Card className="flex items-center gap-3 p-4">
              <div className="flex items-center gap-2 text-sm text-ink-2">
                <span className="h-2 w-2 animate-pulse-glow rounded-full bg-accent" />
                <span>
                  Generating {selected.length} document{selected.length === 1 ? "" : "s"}:
                  {selected.map((d) => titleCase(d).replace("_", " ")).join(", ")}…
                </span>
              </div>
            </Card>
          )}

          {result && <GeneratedDocPanel documents={result.documents} repoId={repoId} repoName={repo?.name} />}
        </>
      )}
    </div>
  );
}
