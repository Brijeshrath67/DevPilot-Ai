import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export interface TooltipProps {
  label: string;
  children: ReactNode;
  side?: "top" | "bottom" | "left" | "right";
  className?: string;
}

const sidePosition: Record<string, string> = {
  top: "bottom-full left-1/2 mb-1.5 -translate-x-1/2",
  bottom: "top-full left-1/2 mt-1.5 -translate-x-1/2",
  left: "right-full top-1/2 mr-1.5 -translate-y-1/2",
  right: "left-full top-1/2 ml-1.5 -translate-y-1/2",
};

export function Tooltip({ label, children, side = "top", className }: TooltipProps) {
  return (
    <span className={cn("group/tooltip relative inline-flex", className)}>
      {children}
      <span
        role="tooltip"
        className={cn(
          "pointer-events-none absolute z-50 whitespace-nowrap rounded-md border border-line-2 bg-panel-4 px-2 py-1 text-[11px] font-medium text-ink-2 opacity-0 shadow-overlay transition-opacity duration-150 group-hover/tooltip:opacity-100",
          sidePosition[side]
        )}
      >
        {label}
      </span>
    </span>
  );
}
