import { useState } from "react";
import { useParams } from "react-router-dom";
import { FlaskConical } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { RunPanel } from "../components/features/RunPanel";
import { AnalyzeGate } from "../components/features/AnalyzeGate";
import { GeneratedTestPanel } from "../components/features/GeneratedTestPanel";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Card } from "../components/ui/Card";
import { Checkbox } from "../components/ui/Checkbox";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useTests } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";
import type { TestsResult } from "../types/api";

const TEST_TYPES = ["unit", "integration", "e2e"];

export function TestingPage() {
  const { repoId } = useParams();
  const { error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const tests = useTests(repoId);

  const [selected, setSelected] = useState<string[]>(["unit"]);
  const [result, setResult] = useState<TestsResult | null>(null);

  const repo = repoQuery.data?.data;
  const loading = repoQuery.isLoading || statusLoading;

  const toggle = (testType: string) => {
    setSelected((prev) =>
      prev.includes(testType) ? prev.filter((t) => t !== testType) : [...prev, testType]
    );
  };

  const run = () => {
    tests.mutate(
      { testTypes: selected },
      {
        onSuccess: (res) => setResult(res.data),
        onError: (err) => toastError(err instanceof Error ? err.message : "Test generation failed."),
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tests"
        description="Generate executable test scaffolds — unit, integration, and end-to-end suites — for the workspace."
        icon={<FlaskConical className="h-5 w-5" />}
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
            icon={<FlaskConical className="h-4 w-4" />}
            title="Test targets"
            description="Choose which test suites to scaffold."
            onRun={run}
            isRunning={tests.isPending}
            disabled={selected.length === 0}
            runLabel={result ? "Re-generate" : "Generate tests"}
            options={
              <div className="flex flex-wrap gap-3">
                {TEST_TYPES.map((testType) => (
                  <Checkbox
                    key={testType}
                    label={`${testType.charAt(0).toUpperCase()}${testType.slice(1)} tests`}
                    checked={selected.includes(testType)}
                    onChange={() => toggle(testType)}
                  />
                ))}
              </div>
            }
          />

          {tests.isPending && (
            <Card className="flex items-center gap-3 p-4">
              <div className="flex items-center gap-2 text-sm text-ink-2">
                <span className="h-2 w-2 animate-pulse-glow rounded-full bg-accent" />
                Generating test scaffolds…
              </div>
            </Card>
          )}

          {result && <GeneratedTestPanel tests={result.tests} />}
        </>
      )}
    </div>
  );
}
