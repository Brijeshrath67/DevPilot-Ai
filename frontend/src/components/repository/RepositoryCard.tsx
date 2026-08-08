import { Link } from "react-router-dom";
import { ArrowUpRight, GitBranch, FolderArchive } from "lucide-react";
import type { Repository } from "../../types/api";
import { Card } from "../ui/Card";
import { RepoStatusBadge } from "./RepoStatusBadge";
import { formatDate } from "../../lib/utils";

export interface RepositoryCardProps {
  repo: Repository;
}

export function RepositoryCard({ repo }: RepositoryCardProps) {
  return (
    <Link to={`/repo/${repo.repository_id}`} className="block">
      <Card interactive className="group flex h-full flex-col justify-between gap-4 p-5">
        <div className="space-y-2.5">
          <div className="flex items-center justify-between gap-2">
            <span className="text-2xs font-medium uppercase tracking-[0.08em] text-ink-3">
              Workspace #{repo.repository_id}
            </span>
            <RepoStatusBadge status={repo.status} />
          </div>
          <h3 className="truncate text-sm font-semibold text-ink transition-colors group-hover:text-accent">
            {repo.name}
          </h3>
          <p className="line-clamp-2 min-h-[2.5rem] text-xs leading-relaxed text-ink-3">
            {repo.summary ||
              (repo.source_url ? `Imported from ${repo.source_url}` : "Workspace ingested successfully.")}
          </p>
        </div>

        <div className="flex items-center justify-between border-t border-line-1 pt-3">
          <span className="flex items-center gap-3 text-[11px] text-ink-3">
            {repo.source_url ? <GitBranch className="h-3.5 w-3.5" /> : <FolderArchive className="h-3.5 w-3.5" />}
            {formatDate(repo.created_at)}
          </span>
          <span className="flex items-center gap-1 text-[11px] font-medium text-ink-2 transition-all duration-150 group-hover:translate-x-0.5 group-hover:text-accent">
            Open workspace
            <ArrowUpRight className="h-3.5 w-3.5" />
          </span>
        </div>
      </Card>
    </Link>
  );
}
