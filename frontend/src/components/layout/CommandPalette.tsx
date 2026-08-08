import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  BookOpen,
  Command,
  FlaskConical,
  HeartPulse,
  LayoutDashboard,
  MessagesSquare,
  ScanSearch,
  Shield,
  ShieldAlert,
  Settings,
} from "lucide-react";
import { Modal } from "../ui/Modal";
import { cn } from "../../lib/utils";

interface Command {
  name: string;
  hint: string;
  path: string;
  icon: ReactNode;
  group: string;
}

export interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const { repoId } = useParams();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands = useMemo<Command[]>(() => {
    const scoped = repoId
      ? [
          { name: "Open Overview", hint: "/repo/:id", path: `/repo/${repoId}`, icon: <ScanSearch className="h-4 w-4" />, group: "Repository" },
          { name: "Run Code Review", hint: "/review", path: `/repo/${repoId}/review`, icon: <ShieldAlert className="h-4 w-4" />, group: "Repository" },
          { name: "Run Security Audit", hint: "/security", path: `/repo/${repoId}/security`, icon: <Shield className="h-4 w-4" />, group: "Repository" },
          { name: "Generate Documentation", hint: "/docs", path: `/repo/${repoId}/docs`, icon: <BookOpen className="h-4 w-4" />, group: "Repository" },
          { name: "Generate Tests", hint: "/tests", path: `/repo/${repoId}/tests`, icon: <FlaskConical className="h-4 w-4" />, group: "Repository" },
          { name: "Open QA Chat", hint: "/chat", path: `/repo/${repoId}/chat`, icon: <MessagesSquare className="h-4 w-4" />, group: "Repository" },
          { name: "Open Health", hint: "/health", path: `/repo/${repoId}/health`, icon: <HeartPulse className="h-4 w-4" />, group: "Repository" },
          { name: "Settings", hint: "/settings", path: `/repo/${repoId}/settings`, icon: <Settings className="h-4 w-4" />, group: "Repository" },
        ]
      : [];
    return [
      { name: "Go to Dashboard", hint: "/", path: "/", icon: <LayoutDashboard className="h-4 w-4" />, group: "General" },
      ...scoped,
    ];
  }, [repoId]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter(
      (c) => c.name.toLowerCase().includes(q) || c.hint.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
    );
  }, [commands, query]);

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setIndex(0);
    const t = window.setTimeout(() => inputRef.current?.focus(), 50);
    return () => window.clearTimeout(t);
  }, [open]);

  useEffect(() => {
    setIndex(0);
  }, [query]);

  useEffect(() => {
    listRef.current?.querySelector<HTMLElement>(`[data-index="${index}"]`)?.scrollIntoView({ block: "nearest" });
  }, [index]);

  if (!open) return null;

  const run = (command: Command) => {
    navigate(command.path);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} size="md" hideClose>
      <div className="overflow-hidden rounded-xl border border-line-1 bg-panel-1 shadow-glow">
        <div className="flex items-center gap-2.5 border-b border-line-1 px-4">
          <Command className="h-4 w-4 shrink-0 text-ink-3" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setIndex((i) => Math.min(i + 1, filtered.length - 1));
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setIndex((i) => Math.max(i - 1, 0));
              } else if (e.key === "Enter" && filtered[index]) {
                run(filtered[index]);
              } else if (e.key === "Escape") {
                onClose();
              }
            }}
            placeholder="Type a command or search…"
            className="w-full bg-transparent py-3.5 text-sm text-ink placeholder:text-ink-3 focus:outline-none"
            aria-label="Command palette"
          />
          <kbd className="hidden rounded border border-line-1 bg-panel-3 px-1.5 py-0.5 font-mono text-2xs text-ink-3 sm:block">
            esc
          </kbd>
        </div>

        <div ref={listRef} className="scrollbar-thin max-h-80 overflow-y-auto p-1.5">
          {filtered.length === 0 && (
            <p className="px-3 py-6 text-center text-sm text-ink-3">No commands found for “{query}”.</p>
          )}
          {["General", "Repository"].map(
            (group) =>
              filtered.some((c) => c.group === group) && (
                <div key={group}>
                  <p className="px-3 pb-1 pt-2 text-2xs font-medium uppercase tracking-[0.1em] text-ink-3">{group}</p>
                  {filtered
                    .filter((c) => c.group === group)
                    .map((command) => {
                      const globalIndex = filtered.indexOf(command);
                      return (
                        <button
                          key={command.name}
                          data-index={globalIndex}
                          onClick={() => run(command)}
                          onMouseEnter={() => setIndex(globalIndex)}
                          className={cn(
                            "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                            globalIndex === index ? "bg-accent/10 text-ink" : "text-ink-2"
                          )}
                        >
                          <span className={cn("shrink-0", globalIndex === index ? "text-accent" : "text-ink-3")}>
                            {command.icon}
                          </span>
                          <span className="flex-1">{command.name}</span>
                          <span className="font-mono text-2xs text-ink-3">{command.hint}</span>
                        </button>
                      );
                    })}
                </div>
              )
          )}
        </div>

        <div className="flex items-center gap-4 border-t border-line-1 px-4 py-2.5 text-2xs text-ink-3">
          <span className="flex items-center gap-1"><kbd className="kbd">↑</kbd><kbd className="kbd">↓</kbd> navigate</span>
          <span className="flex items-center gap-1"><kbd className="kbd">↵</kbd> select</span>
          <span className="ml-auto font-mono">devpilot ⌘K</span>
        </div>
      </div>
    </Modal>
  );
}
