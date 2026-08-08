import { useMemo } from "react";
import { useParams } from "react-router-dom";
import { Check, Copy, FolderGit2, Info, RefreshCw, Settings } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository, useRepositoryFiles } from "../hooks/useRepository";
import { useRepoStatus } from "../hooks/useRepoStatus";
import { useAnalyze } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";

function InfoRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5">
      <span className="shrink-0 text-xs font-medium uppercase tracking-[0.08em] text-ink-3">{label}</span>
      <span className={`min-w-0 truncate text-right text-[13px] text-ink-2 ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}

export function SettingsPage() {
  const { repoId } = useParams();
  const { success: toastSuccess, info: toastInfo, error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const filesQuery = useRepositoryFiles(repoId);
  const { status } = useRepoStatus(repoId);
  const analyze = useAnalyze(repoId);

  const repo = repoQuery.data?.data;
  const files = useMemo(() => filesQuery.data?.data ?? [], [filesQuery.data]);

  const languageCount = useMemo(() => {
    const set = new Set<string>();
    for (const file of files) if (file.language) set.add(file.language);
    return set.size;
  }, [files]);

  const copy = async (value: string) => {
    await navigator.clipboard.writeText(value);
    toastSuccess("Copied to clipboard");
  };

  if (repoQuery.isLoading) {
    return (
      <Card className="p-5">
        <SkeletonLines lines={6} />
      </Card>
    );
  }

  if (!repo) {
    return (
      <Card className="p-4">
        <p className="py-10 text-center text-sm text-ink-3">Repository not found.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workspace settings"
        description="Repository metadata and workspace controls."
        icon={<Settings className="h-5 w-5" />}
        badge={<RepoStatusBadge status={status ?? repo.status} />}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <div className="mb-2 flex items-center gap-2">
            <Info className="h-3.5 w-3.5 text-accent" />
            <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Repository info</h2>
          </div>
          <div className="divide-y divide-line-1">
            <InfoRow label="Name" value={repo.name} />
            <InfoRow label="Workspace ID" value={`#${repo.repository_id}`} mono />
            <InfoRow label="Source" value={repo.source_url ?? "Uploaded archive"} mono />
            <InfoRow label="Root path" value={repo.root_path ?? "—"} mono />
            <InfoRow label="Status" value={status ?? repo.status} />
            <InfoRow label="Indexed files" value={String(files.length)} />
            <InfoRow label="Languages" value={String(languageCount)} />
          </div>
        </Card>

        <div className="space-y-4">
          <Card className="p-5">
            <div className="mb-2 flex items-center gap-2">
              <FolderGit2 className="h-3.5 w-3.5 text-accent" />
              <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Workspace ID</h2>
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-line-2 bg-panel-1 px-3 py-2.5">
              <span className="flex-1 truncate font-mono text-xs text-ink-2">{repo.repository_id}</span>
              <Button size="sm" variant="ghost" icon={<Copy className="h-3.5 w-3.5" />} onClick={() => copy(String(repo.repository_id))}>
                Copy
              </Button>
            </div>
            <p className="mt-2 text-xs text-ink-3">Use this ID with the API to target this workspace.</p>
          </Card>

          <Card className="p-5">
            <div className="mb-2 flex items-center gap-2">
              <RefreshCw className="h-3.5 w-3.5 text-accent" />
              <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Analysis</h2>
            </div>
            <p className="text-[13px] leading-relaxed text-ink-3">
              Re-running analysis re-scans the workspace, re-embeds the codebase, and refreshes the project summary.
            </p>
            <Button
              size="sm"
              variant="secondary"
              className="mt-3"
              icon={<Check className="h-3.5 w-3.5" />}
              loading={analyze.isPending}
              onClick={() =>
                analyze.mutate("full", {
                  onSuccess: () => toastInfo("Analysis started — this may take a moment."),
                  onError: (err) => toastError(err instanceof Error ? err.message : "Analysis failed."),
                })
              }
            >
              Re-run analysis
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}
