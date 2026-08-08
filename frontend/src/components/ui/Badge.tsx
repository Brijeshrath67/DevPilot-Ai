import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export type BadgeTone = "neutral" | "accent" | "success" | "warning" | "critical" | "info";

const toneStyles: Record<BadgeTone, string> = {
  neutral: "bg-panel-3 text-ink-2 border-line-2",
  accent: "bg-accent/10 text-accent border-accent/25",
  success: "bg-success/10 text-success border-success/25",
  warning: "bg-warning/10 text-warning border-warning/25",
  critical: "bg-critical/10 text-critical border-critical/25",
  info: "bg-info/10 text-info border-info/25",
};

export interface BadgeProps {
  tone?: BadgeTone;
  className?: string;
  children: ReactNode;
}

export function Badge({ tone = "neutral", className, children }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] font-medium leading-none",
        toneStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
