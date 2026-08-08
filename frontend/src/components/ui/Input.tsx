import type { InputHTMLAttributes, TextareaHTMLAttributes, ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Field({
  label,
  hint,
  children,
}: {
  label?: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block space-y-1.5">
      {label && (
        <span className="block text-2xs font-semibold uppercase tracking-[0.08em] text-ink-3">
          {label}
        </span>
      )}
      {children}
      {hint && <span className="block text-xs text-ink-3">{hint}</span>}
    </label>
  );
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-9 w-full rounded-lg border border-line-2 bg-panel-1 px-3 text-sm text-ink placeholder:text-ink-3",
        "transition-all duration-150 focus:border-accent/60 focus:shadow-[0_0_0_3px_rgba(99,102,241,0.12)]",
        "outline-none",
        className
      )}
      {...props}
    />
  );
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "w-full rounded-lg border border-line-2 bg-panel-1 px-3 py-2 text-sm text-ink placeholder:text-ink-3",
        "transition-all duration-150 focus:border-accent/60 focus:shadow-[0_0_0_3px_rgba(99,102,241,0.12)]",
        "outline-none",
        className
      )}
      {...props}
    />
  );
}
