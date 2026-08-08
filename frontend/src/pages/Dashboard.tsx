import { useState } from "react";
import { FolderGit2, Layers, Loader2, Plus, ScanSearch } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { NewRepositoryModal } from "../components/features/NewRepositoryModal";
import { RepositoryCard } from "../components/repository/RepositoryCard";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepositories } from "../hooks/useRepositories";
import type { Repository } from "../types/api";

function statCards(repos: Repository[]) {
  const analyzing = repos.filter((r) => r.status === "analyzing").length;
  const analyzed = repos.filter((r) => r.status === "analyzed").length;
  const pending = repos.filter((r) => r.status === "pending").length;
  const errored = repos.filter((r) => r.status === "error").length;
  return [
    { label: "Total workspaces", value: repos.length, tone: "text-ink", icon: <Layers className="h-4 w-4" /> },
    { label: "Analyzed", value: analyzed, tone: "text-success", icon: <ScanSearch className="h-4 w-4" /> },
    { label: "Processing", value: pending + analyzing, tone: "text-warning", icon: <Loader2 className="h-4 w-4" /> },
    { label: "Failed", value: errored, tone: "text-critical", icon: <FolderGit2 className="h-4 w-4" /> },
  ];
}

export function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useRepositories();
  const [modalOpen, setModalOpen] = useState(false);
  const repos = data?.data ?? [];
  const stats = statCards(repos);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workspaces"
        description="Import a GitHub repository or ZIP archive, then run AI-driven reviews, audits, documentation, tests, and chat with your code."
        icon={<Layers className="h-5 w-5" />}
        actions={
          <Button size="sm" icon={<Plus className="h-3.5 w-3.5" />} onClick={() => setModalOpen(true)}>
            New workspace
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="flex items-center gap-3 p-4">
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-panel-3 text-ink-3">{stat.icon}</div>
            <div className="min-w-0">
              <p className={`text-lg font-semibold leading-none ${stat.tone}`}>{stat.value}</p>
              <p className="mt-1 truncate text-2xs font-medium uppercase tracking-[0.08em] text-ink-3">{stat.label}</p>
            </div>
          </Card>
        ))}
      </div>

      {isLoading ? (
        <Card className="p-5">
          <SkeletonLines lines={3} />
        </Card>
      ) : isError ? (
        <Card className="p-8 text-center">
          <p className="text-sm font-medium text-critical">Could not load workspaces</p>
          <p className="mt-1 text-xs text-ink-3">{error instanceof Error ? error.message : "Unknown error"}</p>
          <Button size="sm" variant="secondary" className="mt-4" onClick={() => refetch()}>
            Retry
          </Button>
        </Card>
      ) : repos.length === 0 ? (
        <Card className="p-4">
          <EmptyState
            icon={<FolderGit2 className="h-5 w-5" />}
            title="No workspaces yet"
            description="Import your first repository to unlock code review, security audits, documentation, tests, and the QA assistant."
            action={
              <Button size="sm" icon={<Plus className="h-3.5 w-3.5" />} onClick={() => setModalOpen(true)}>
                Import a repository
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {repos.map((repo) => (
            <RepositoryCard key={repo.repository_id} repo={repo} />
          ))}
        </div>
      )}

      <NewRepositoryModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
