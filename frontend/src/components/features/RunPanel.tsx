import type { ReactNode } from "react";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { cn } from "../../lib/utils";

export interface RunPanelProps {
  icon: ReactNode;
  title: string;
  description: string;
  options?: ReactNode;
  onRun: () => void;
  isRunning: boolean;
  disabled?: boolean;
  runLabel?: string;
  footer?: ReactNode;
  className?: string;
}

export function RunPanel({
  icon,
  title,
  description,
  options,
  onRun,
  isRunning,
  disabled,
  runLabel = "Run",
  footer,
  className,
}: RunPanelProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="flex items-start gap-3 border-b border-line-1 px-5 py-4">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent">{icon}</div>
        <div className="space-y-0.5">
          <h2 className="text-sm font-semibold text-ink">{title}</h2>
          <p className="max-w-xl text-xs leading-relaxed text-ink-3">{description}</p>
        </div>
      </div>
      {options && <div className="border-b border-line-1 px-5 py-4">{options}</div>}
      <div className="flex items-center justify-between gap-3 px-5 py-3.5">
        <div className="min-w-0">{footer}</div>
        <Button onClick={onRun} loading={isRunning} disabled={disabled} icon={undefined} className="shrink-0">
          {runLabel}
        </Button>
      </div>
    </Card>
  );
}
