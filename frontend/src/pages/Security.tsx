import { useState } from "react";
import { useParams } from "react-router-dom";
import { Shield } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { RunPanel } from "../components/features/RunPanel";
import { AnalyzeGate } from "../components/features/AnalyzeGate";
import { FindingList } from "../components/features/FindingList";
import { RecommendationsList } from "../components/features/RecommendationsList";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Card } from "../components/ui/Card";
import { ScoreRing } from "../components/ui/ScoreRing";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useSecurityAudit } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";
import { scoreVerdict } from "../lib/utils";
import type { SecurityResult } from "../types/api";

export function SecurityPage() {
  const { repoId } = useParams();
  const { error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const audit = useSecurityAudit(repoId);

  const [result, setResult] = useState<SecurityResult | null>(null);

  const repo = repoQuery.data?.data;
  const loading = repoQuery.isLoading || statusLoading;

  const run = () => {
    audit.mutate(undefined, {
      onSuccess: (res) => setResult(res.data),
      onError: (err) => toastError(err instanceof Error ? err.message : "Security audit failed."),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security audit"
        description="Rule-based vulnerability scan across the codebase — secrets, path traversal, unsafe functions, and injection risks."
        icon={<Shield className="h-5 w-5" />}
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
            icon={<Shield className="h-4 w-4" />}
            title="Audit configuration"
            description="Run a full vulnerability scan over every indexed file."
            onRun={run}
            isRunning={audit.isPending}
            runLabel={result ? "Re-run audit" : "Run security audit"}
            footer={
              <span className="text-xs text-ink-3">
                Detects leaked keys, risky function calls, injection patterns, and path traversal.
              </span>
            }
          />

          {audit.isPending && (
            <Card className="flex items-center gap-3 p-4">
              <div className="flex items-center gap-2 text-sm text-ink-2">
                <span className="h-2 w-2 animate-pulse-glow rounded-full bg-accent" />
                Scanning for vulnerabilities…
              </div>
            </Card>
          )}

          {result && (
            <div className="animate-fade-in-up space-y-4">
              <div className="grid gap-3 lg:grid-cols-3">
                <Card className="flex items-center justify-center p-6">
                  <ScoreRing
                    value={result.security_score}
                    size={150}
                    label="Score"
                    sublabel={scoreVerdict(result.security_score)}
                  />
                </Card>
                <Card className="p-5 lg:col-span-2">
                  <h2 className="mb-3 text-sm font-semibold text-ink">Findings summary</h2>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                    {(
                      [
                        ["Critical", result.issues.filter((i) => i.severity === "CRITICAL").length],
                        ["High", result.issues.filter((i) => i.severity === "HIGH").length],
                        ["Medium", result.issues.filter((i) => i.severity === "MEDIUM").length],
                        ["Minor", result.issues.filter((i) => i.severity === "MINOR").length],
                      ] as const
                    ).map(([label, count]) => (
                      <div key={label} className="rounded-lg bg-panel-1 px-3 py-2.5">
                        <p className="text-lg font-semibold tabular-nums text-ink">{count}</p>
                        <p className="text-2xs font-medium uppercase tracking-[0.08em] text-ink-3">{label}</p>
                      </div>
                    ))}
                  </div>
                  <p className="mt-3 text-xs text-ink-3">
                    Scanned {result.files_scanned.toLocaleString()} file{result.files_scanned === 1 ? "" : "s"} across{" "}
                    {result.patterns_checked} patterns in {result.scan_time_ms} ms.
                  </p>
                </Card>
              </div>

              <div>
                <h2 className="mb-2.5 text-sm font-semibold text-ink">Vulnerabilities</h2>
                <FindingList findings={result.issues} />
              </div>

              <RecommendationsList recommendations={result.recommendations} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
