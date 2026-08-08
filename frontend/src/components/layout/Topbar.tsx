import { Link, useLocation, useParams } from "react-router-dom";
import { Command, Menu, Moon, Plus, Sun } from "lucide-react";
import { useTheme } from "../../hooks/useTheme";
import { IconButton } from "../ui/IconButton";
import { Button } from "../ui/Button";
import { RepoStatusBadge } from "../repository/RepoStatusBadge";
import { useRepository } from "../../hooks/useRepository";
import { Tooltip } from "../ui/Tooltip";
import { cn } from "../../lib/utils";

function pageLabel(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return "Dashboard";
  if (segments[0] === "repo") {
    const page = segments[2];
    const map: Record<string, string> = {
      review: "Code Review",
      security: "Security Audit",
      docs: "Documentation",
      tests: "Tests",
      chat: "QA Chat",
      health: "Health",
      settings: "Settings",
    };
    return page ? (map[page] ?? "Overview") : "Overview";
  }
  return "Dashboard";
}

export interface TopbarProps {
  onMenuClick: () => void;
  onOpenCommand: () => void;
}

export function Topbar({ onMenuClick, onOpenCommand }: TopbarProps) {
  const { repoId } = useParams();
  const location = useLocation();
  const { theme, toggle } = useTheme();
  const { data } = useRepository(repoId);
  const repo = data?.data;

  const crumbs = [
    { label: "repos", href: "/" },
    ...(repo ? [{ label: repo.name, href: `/repo/${repo.repository_id}` }] : []),
    { label: pageLabel(location.pathname), href: null as string | null },
  ];

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-line-1 bg-panel-1/80 px-4 backdrop-blur-md sm:px-6">
      <IconButton label="Open navigation" className="lg:hidden" onClick={onMenuClick}>
        <Menu className="h-4 w-4" />
      </IconButton>

      <nav aria-label="Breadcrumb" className="flex min-w-0 flex-1 items-center gap-1.5 text-xs">
        {crumbs.map((crumb, index) => (
          <span key={index} className="flex min-w-0 items-center gap-1.5">
            {index > 0 && <span className="text-ink-3/50">/</span>}
            {crumb.href ? (
              <Link
                to={crumb.href}
                className="max-w-[160px] truncate font-medium text-ink-3 transition-colors hover:text-ink"
              >
                {crumb.label}
              </Link>
            ) : (
              <span className="max-w-[200px] truncate font-medium text-ink">{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>

      <div className="flex shrink-0 items-center gap-2">
        {repo && <RepoStatusBadge status={repo.status} className="hidden sm:inline-flex" />}

        <Tooltip label="Toggle theme" side="bottom">
          <IconButton label="Toggle theme" onClick={toggle}>
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </IconButton>
        </Tooltip>

        <Tooltip label="Command palette" side="bottom">
          <IconButton label="Open command palette" onClick={onOpenCommand} className="hidden sm:inline-flex">
            <Command className="h-4 w-4" />
          </IconButton>
        </Tooltip>

        <Link to="/">
          <Button size="sm" icon={<Plus className="h-3.5 w-3.5" />} className={cn("whitespace-nowrap")}>
            <span className="hidden sm:inline">New repository</span>
          </Button>
        </Link>
      </div>
    </header>
  );
}
