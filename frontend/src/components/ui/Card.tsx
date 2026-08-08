import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../lib/utils";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
}

export function Card({ interactive, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl2 border border-line-1 bg-panel-2",
        interactive &&
          "cursor-pointer transition-all duration-150 ease-out hover:-translate-y-px hover:border-line-3 hover:bg-panel-3",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-start justify-between gap-4 border-b border-line-1 px-5 py-4", className)}>
      <div className="space-y-0.5">
        <h3 className="text-sm font-semibold text-ink">{title}</h3>
        {description && <p className="text-xs text-ink-3">{description}</p>}
      </div>
      {action}
    </div>
  );
}
