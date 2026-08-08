import { useState } from "react";
import { AlertTriangle, ChevronDown, FileCode2, Lightbulb } from "lucide-react";
import type { Finding } from "../../types/api";
import { Badge, type BadgeTone } from "../ui/Badge";
import { cn } from "../../lib/utils";

// eslint-disable-next-line react-refresh/only-export-components
export function severityTone(severity: Finding["severity"]): BadgeTone {
  switch (severity) {
    case "CRITICAL":
      return "critical";
    case "HIGH":
      return "critical";
    case "MEDIUM":
      return "warning";
    default:
      return "info";
  }
}

// eslint-disable-next-line react-refresh/only-export-components
export function severityRank(severity: Finding["severity"]): number {
  switch (severity) {
    case "CRITICAL":
      return 4;
    case "HIGH":
      return 3;
    case "MEDIUM":
      return 2;
    default:
      return 1;
  }
}

export interface FindingListProps {
  findings: Finding[];
  className?: string;
}

export function FindingList({ findings, className }: FindingListProps) {
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set([0]));
  const sorted = [...findings].sort((a, b) => severityRank(b.severity) - severityRank(a.severity));

  if (findings.length === 0) {
    return (
      <div className={cn("rounded-xl border border-line-1 bg-panel-2 px-5 py-8 text-center", className)}>
        <div className="mx-auto mb-2 grid h-10 w-10 place-items-center rounded-full bg-success/10 text-success">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <p className="text-sm font-medium text-ink">No issues found</p>
        <p className="mt-0.5 text-xs text-ink-3">The scan completed without flagging any issues.</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {sorted.map((finding, index) => {
        const open = expanded.has(index);
        return (
          <div
            key={`${finding.file}:${finding.line}:${index}`}
            className={cn(
              "overflow-hidden rounded-xl border bg-panel-2 transition-colors",
              open ? "border-line-2" : "border-line-1"
            )}
          >
            <button
              className="flex w-full items-center gap-3 px-4 py-3 text-left"
              onClick={() =>
                setExpanded((prev) => {
                  const next = new Set(prev);
                  if (next.has(index)) next.delete(index);
                  else next.add(index);
                  return next;
                })
              }
              aria-expanded={open}
            >
              <Badge tone={severityTone(finding.severity)} className="w-20 shrink-0 justify-center">
                {finding.severity}
              </Badge>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[13px] font-medium text-ink">{finding.vulnerability}</p>
                <p className="flex items-center gap-1 truncate font-mono text-2xs text-ink-3">
                  <FileCode2 className="h-3 w-3 shrink-0" />
                  {finding.file}
                  {finding.line > 0 && <span className="text-ink-3/70">:{finding.line}</span>}
                </p>
              </div>
              <ChevronDown className={cn("h-4 w-4 shrink-0 text-ink-3 transition-transform", open && "rotate-180")} />
            </button>
            {open && (
              <div className="animate-fade-in space-y-3 border-t border-line-1 px-4 py-3">
                <p className="text-[13px] leading-relaxed text-ink-2">{finding.description}</p>
                <div className="flex gap-2.5 rounded-lg bg-accent-soft/60 px-3 py-2.5">
                  <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" />
                  <p className="text-xs leading-relaxed text-ink-2">{finding.recommendation}</p>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
