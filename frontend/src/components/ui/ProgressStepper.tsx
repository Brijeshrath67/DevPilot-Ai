import { Check, Circle } from "lucide-react";
import { cn } from "../../lib/utils";

export interface ProgressStep {
  label: string;
}

export interface ProgressStepperProps {
  steps: ProgressStep[];
  current: number;
  className?: string;
}

export function ProgressStepper({ steps, current, className }: ProgressStepperProps) {
  return (
    <ol className={cn("space-y-3", className)} aria-label="Analysis progress">
      {steps.map((step, index) => {
        const done = index < current;
        const active = index === current;
        return (
          <li key={step.label} className="flex items-center gap-3">
            <span
              className={cn(
                "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] font-semibold transition-all duration-200",
                done && "border-success/40 bg-success/10 text-success",
                active &&
                  "animate-pulse-glow border-accent/50 bg-accent/15 text-accent shadow-[0_0_12px_rgba(99,102,241,0.25)]",
                !done && !active && "border-line-3 text-ink-3"
              )}
            >
              {done ? <Check className="h-3 w-3" strokeWidth={3} /> : active ? <Circle className="h-2 w-2 fill-current" /> : index + 1}
            </span>
            <span
              className={cn(
                "text-sm transition-colors duration-200",
                done && "text-ink-2",
                active && "font-medium text-ink",
                !done && !active && "text-ink-3"
              )}
            >
              {step.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
