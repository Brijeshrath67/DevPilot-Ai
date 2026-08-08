import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
}

export function IconButton({ label, className, children, ...props }: IconButtonProps) {
  return (
    <button
      aria-label={label}
      title={label}
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-lg text-ink-3",
        "transition-all duration-150 hover:text-ink hover:bg-panel-3",
        "focus-visible:outline-2 focus-visible:outline-accent",
        "disabled:opacity-40 disabled:pointer-events-none",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
