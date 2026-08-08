import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Boxes,
  Braces,
  FolderTree,
  Package,
  RefreshCw,
  ScanSearch,
  Sparkles,
} from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { FileExplorer } from "../components/repository/FileExplorer";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Card, CardHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Modal } from "../components/ui/Modal";
import { ProgressStepper } from "../components/ui/ProgressStepper";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository, useRepositoryFiles } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useAnalyze } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";

const MANIFEST_PATTERNS = [
  "package.json",
  "pyproject.toml",
  "requirements.txt",
  "setup.py",
  "go.mod",
  "Cargo.toml",
  "pom.xml",
  "build.gradle",
  "Gemfile",
  "composer.json",
  "Pipfile",
  "cargo.lock",
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
];

const STEPS = [
  { label: "Fetching repository" },
  { label: "Scanning structure & files" },
  { label: "Embedding codebase" },
  { label: "Generating summary" },
];

export function RepositoryOverviewPage() {
  const { repoId } = useParams();
  const { info: toastInfo, error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const filesQuery = useRepositoryFiles(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const analyze = useAnalyze(repoId);
  const [depsOpen, setDepsOpen] = useState(false);

  const repo = repoQuery.data?.data;
  const files = useMemo(() => filesQuery.data?.data ?? [], [filesQuery.data]);

  const languages = useMemo(() => {
    const counts = new Map<string, number>();
    for (const file of files) {
      if (!file.language) continue;
      counts.set(file.language, (counts.get(file.language) ?? 0) + 1);
    }
    return Array.from(counts.entries())
      .map(([language, count]) => ({ language, count }))
      .sort((a, b) => b.count - a.count);
  }, [files]);

  const manifests = useMemo(() => {
    const lower = files.map((f) => f.file_path);
    return MANIFEST_PATTERNS.filter((m) => lower.includes(m));
  }, [files]);

  const processing = isProcessing(status);
  const loading = repoQuery.isLoading || statusLoading;

  const runAnalysis = () => {
    analyze.mutate("full", {
      onSuccess: () => toastInfo("Analysis started — this may take a moment."),
      onError: (err) => toastError(err instanceof Error ? err.message : "Analysis failed."),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={repo?.name ?? "Repository overview"}
        description={repo?.source_url ?? "Inspect the workspace structure and run analysis."}
        icon={<ScanSearch className="h-5 w-5" />}
        badge={repo ? <RepoStatusBadge status={status ?? repo.status} /> : undefined}
        actions={
          repo &&
          !processing && (
            <Button
              size="sm"
              variant="secondary"
              icon={<RefreshCw className="h-3.5 w-3.5" />}
              onClick={runAnalysis}
              loading={analyze.isPending}
            >
              Re-run analysis
            </Button>
          )
        }
      />

      {loading ? (
        <Card className="p-5">
          <SkeletonLines lines={5} />
        </Card>
      ) : !repo ? (
        <Card className="p-4">
          <EmptyState icon={<ScanSearch className="h-5 w-5" />} title="Repository not found" />
        </Card>
      ) : processing ? (
        <Card className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_240px]">
          <div className="space-y-1">
            <h2 className="text-sm font-semibold text-ink">Analyzing workspace</h2>
            <p className="text-xs text-ink-3">
              Indexing files and generating a project summary. You can leave this page and come back.
            </p>
          </div>
          <ProgressStepper steps={STEPS} current={status === "analyzing" ? 1 : 0} />
        </Card>
      ) : status === "error" ? (
        <Card className="p-4">
          <EmptyState
            icon={<ScanSearch className="h-5 w-5" />}
            title="Analysis failed"
            description="The previous analysis run errored. Try running it again."
            action={
              <Button size="sm" icon={<RefreshCw className="h-3.5 w-3.5" />} onClick={runAnalysis} loading={analyze.isPending}>
                Retry analysis
              </Button>
            }
          />
        </Card>
      ) : status !== "analyzed" ? (
        <Card className="p-4">
          <EmptyState
            icon={<ScanSearch className="h-5 w-5" />}
            title="Not analyzed yet"
            description="Run analysis to index the workspace and unlock every DevPilot feature."
            action={
              <Button size="sm" icon={<Sparkles className="h-3.5 w-3.5" />} onClick={runAnalysis} loading={analyze.isPending}>
                Run analysis
              </Button>
            }
          />
        </Card>
      ) : (
        <>
          {(repo.summary || repo.architecture_summary) && (
            <div className="grid gap-3 lg:grid-cols-2">
              {repo.summary && (
                <Card className="p-5">
                  <div className="mb-2 flex items-center gap-2">
                    <Sparkles className="h-3.5 w-3.5 text-accent" />
                    <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Project summary</h2>
                  </div>
                  <p className="text-[13px] leading-relaxed text-ink-2">{repo.summary}</p>
                </Card>
              )}
              {repo.architecture_summary && (
                <Card className="p-5">
                  <div className="mb-2 flex items-center gap-2">
                    <Boxes className="h-3.5 w-3.5 text-accent2" />
                    <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Architecture</h2>
                  </div>
                  <p className="text-[13px] leading-relaxed text-ink-2">{repo.architecture_summary}</p>
                </Card>
              )}
            </div>
          )}

          <div className="grid gap-3 lg:grid-cols-3">
            <Card className="p-5 lg:col-span-2">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Braces className="h-3.5 w-3.5 text-info" />
                  <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Languages</h2>
                </div>
              </div>
              {languages.length === 0 ? (
                <p className="text-xs text-ink-3">No languages detected.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {languages.map(({ language, count }) => (
                    <Badge key={language} tone="info">
                      {language}
                      <span className="ml-0.5 text-ink-3">· {count}</span>
                    </Badge>
                  ))}
                </div>
              )}
            </Card>

            <Card className="flex flex-col justify-between p-5">
              <div className="mb-3 flex items-center gap-2">
                <Package className="h-3.5 w-3.5 text-accent" />
                <h2 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Dependencies</h2>
              </div>
              <p className="text-xs text-ink-3">
                {manifests.length > 0
                  ? `${manifests.length} manifest file${manifests.length > 1 ? "s" : ""} detected.`
                  : "No dependency manifests detected."}
              </p>
              <Button
                size="sm"
                variant="secondary"
                className="mt-4"
                disabled={manifests.length === 0}
                onClick={() => setDepsOpen(true)}
              >
                View manifests
              </Button>
            </Card>
          </div>

          <CardHeader
            title="File explorer"
            description={`${files.length} files indexed`}
            action={
              <span className="flex items-center gap-1.5 text-2xs font-medium uppercase tracking-[0.08em] text-ink-3">
                <FolderTree className="h-3.5 w-3.5" />
                Browse
              </span>
            }
          />
          <FileExplorer files={files} repoId={repoId} loading={filesQuery.isLoading} />
        </>
      )}

      <Modal open={depsOpen} onClose={() => setDepsOpen(false)} title="Dependency manifests" description="Manifest files detected during indexing.">
        <div className="scrollbar-thin max-h-72 overflow-y-auto p-5">
          <ul className="space-y-1.5">
            {manifests.map((manifest) => (
              <li key={manifest} className="flex items-center gap-2 rounded-lg bg-panel-1 px-3 py-2 font-mono text-xs text-ink-2">
                <Package className="h-3.5 w-3.5 shrink-0 text-ink-3" />
                {manifest}
              </li>
            ))}
          </ul>
        </div>
      </Modal>
    </div>
  );
}
