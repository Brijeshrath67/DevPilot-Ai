import { NavLink, useParams } from "react-router-dom";
import type { ReactNode } from "react";
import {
  BookOpen,
  FlaskConical,
  HeartPulse,
  LayoutDashboard,
  MessagesSquare,
  ScanSearch,
  Settings,
  Shield,
  ShieldAlert,
  X,
} from "lucide-react";
import { Logo } from "./Logo";
import { IconButton } from "../ui/IconButton";
import { cn } from "../../lib/utils";

interface NavItem {
  name: string;
  path: string;
  icon: ReactNode;
  scoped: boolean;
}

export interface SidebarProps {
  onNavigate?: () => void;
}

export function Sidebar({ onNavigate }: SidebarProps) {
  const { repoId } = useParams();

  const items: NavItem[] = [
    { name: "Dashboard", path: "/", icon: <LayoutDashboard className="h-4 w-4" />, scoped: false },
    { name: "Overview", path: `/repo/${repoId}`, icon: <ScanSearch className="h-4 w-4" />, scoped: true },
    { name: "Code Review", path: `/repo/${repoId}/review`, icon: <ShieldAlert className="h-4 w-4" />, scoped: true },
    { name: "Security", path: `/repo/${repoId}/security`, icon: <Shield className="h-4 w-4" />, scoped: true },
    { name: "Documentation", path: `/repo/${repoId}/docs`, icon: <BookOpen className="h-4 w-4" />, scoped: true },
    { name: "Tests", path: `/repo/${repoId}/tests`, icon: <FlaskConical className="h-4 w-4" />, scoped: true },
    { name: "QA Chat", path: `/repo/${repoId}/chat`, icon: <MessagesSquare className="h-4 w-4" />, scoped: true },
    { name: "Health", path: `/repo/${repoId}/health`, icon: <HeartPulse className="h-4 w-4" />, scoped: true },
    { name: "Settings", path: `/repo/${repoId}/settings`, icon: <Settings className="h-4 w-4" />, scoped: true },
  ];

  return (
    <aside className="flex h-full w-60 flex-col border-r border-line-1 bg-panel-1">
      <div className="flex items-center justify-between border-b border-line-1 px-5 py-4">
        <div className="flex items-center gap-2.5">
          <Logo size={26} />
          <div className="leading-tight">
            <span className="block text-sm font-semibold text-ink">DevPilot AI</span>
            <span className="block text-2xs font-medium uppercase tracking-[0.12em] text-ink-3">
              Productivity suite
            </span>
          </div>
        </div>
        <IconButton label="Close navigation" className="md:hidden" onClick={onNavigate}>
          <X className="h-4 w-4" />
        </IconButton>
      </div>

      <nav className="scrollbar-thin flex-1 space-y-0.5 overflow-y-auto px-3 py-4" aria-label="Primary">
        {items.map((item) => {
          const disabled = item.scoped && !repoId;
          return (
            <NavLink
              key={item.name}
              to={disabled ? "/" : item.path}
              onClick={(e) => {
                if (disabled) e.preventDefault();
                onNavigate?.();
              }}
              aria-disabled={disabled}
              title={disabled ? "Import or open a repository to use this feature" : undefined}
              className={({ isActive }) =>
                cn(
                  "group relative flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-all duration-150",
                  disabled && "cursor-not-allowed opacity-40",
                  isActive && !disabled
                    ? "bg-accent/10 text-accent shadow-[inset_0_0_0_1px_rgba(99,102,241,0.18)]"
                    : "text-ink-3 hover:bg-panel-3 hover:text-ink-2"
                )
              }
            >
              {({ isActive }) => (
                <>
                  <span className={cn("transition-colors", isActive && !disabled ? "text-accent" : "text-ink-3 group-hover:text-ink-2")}>
                    {item.icon}
                  </span>
                  <span>{item.name}</span>
                  {isActive && !disabled && (
                    <span className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-accent shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-line-1 px-5 py-4">
        <div className="flex items-center gap-2 text-2xs text-ink-3">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
          </span>
          <span>System operational</span>
        </div>
        <p className="mt-1.5 font-mono text-2xs text-ink-3/70">v1.0.0</p>
      </div>
    </aside>
  );
}
