import { useState } from "react";
import { useParams } from "react-router-dom";
import { HeartPulse, RefreshCw } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { AnalyzeGate } from "../components/features/AnalyzeGate";
import { RecommendationsList } from "../components/features/RecommendationsList";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ScoreRing } from "../components/ui/ScoreRing";
import { ScoreBar } from "../components/ui/ScoreBar";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useProjectHealth } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";
import { scoreVerdict } from "../lib/utils";
import type { HealthResult } from "../types/api";

const DIMENSIONS: Array<{ key: keyof HealthResult; label: string; hint: string }> = [
  { key: "documentation_score", label: "Documentation", hint: "Coverage of docs & inline comments" },
  { key: "testing_score", label: "Testing", hint: "Presence and breadth of test suites" },
  { key: "security_score", label: "Security", hint: "Exposure to vulnerabilities and risky patterns" },
  { key: "maintainability_score", label: "Maintainability", hint: "Structure, conventions, and readability" },
  { key: "complexity_score", label: "Complexity", hint: "Cyclomatic complexity of the codebase" },
];

export function HealthPage() {
  const { repoId } = useParams();
  const { error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const health = useProjectHealth(repoId);

  const [result, setResult] = useState<HealthResult | null>(null);

  const repo = repoQuery.data?.data;
  const loading = repoQuery.isLoading || statusLoading;

  const check = () => {
    health.mutate(undefined, {
      onSuccess: (res) => setResult(res.data),
      onError: (err) => toastError(err instanceof Error ? err.message : "Health check failed."),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Project health"
        description="A multi-dimensional health score derived from documentation, testing, security, maintainability, and complexity."
        icon={<HeartPulse className="h-5 w-5" />}
        badge={repo ? <RepoStatusBadge status={status ?? repo.status} /> : undefined}
        actions={
          <Button
            size="sm"
            variant="secondary"
            icon={<RefreshCw className="h-3.5 w-3.5" />}
            onClick={check}
            loading={health.isPending}
          >
            {result ? "Re-check health" : "Check health"}
          </Button>
        }
      />

      {loading ? (
        <Card className="p-5">
          <SkeletonLines lines={5} />
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
      ) : !result ? (
        <Card className="p-8">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-xl bg-accent/10 text-accent">
              <HeartPulse className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-ink">No health report yet</p>
              <p className="mx-auto max-w-sm text-xs leading-relaxed text-ink-3">
                Run a health check to see a scored report across the five quality dimensions.
              </p>
            </div>
            <Button size="sm" icon={<RefreshCw className="h-3.5 w-3.5" />} onClick={check} loading={health.isPending}>
              Check health
            </Button>
          </div>
        </Card>
      ) : (
        <div className="animate-fade-in-up space-y-4">
          <div className="grid gap-3 lg:grid-cols-3">
            <Card className="flex items-center justify-center p-6">
              <ScoreRing
                value={result.overall_score}
                size={170}
                label="Overall"
                sublabel={scoreVerdict(result.overall_score)}
              />
            </Card>

            <Card className="p-5 lg:col-span-2">
              <h2 className="mb-4 text-sm font-semibold text-ink">Score breakdown</h2>
              <div className="space-y-4">
                {DIMENSIONS.map((dimension) => (
                  <div key={dimension.key}>
                    <ScoreBar label={dimension.label} value={result[dimension.key] as number} />
                    <p className="mt-0.5 text-2xs text-ink-3">{dimension.hint}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <RecommendationsList recommendations={result.recommendations} />
        </div>
      )}
    </div>
  );
}
