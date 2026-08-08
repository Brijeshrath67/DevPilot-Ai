import type { InputHTMLAttributes } from "react";
import { Check } from "lucide-react";
import { cn } from "../../lib/utils";

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "size"> {
  label?: string;
}

export function Checkbox({ label, className, ...props }: CheckboxProps) {
  return (
    <label
      className={cn(
        "group inline-flex cursor-pointer select-none items-center gap-2.5",
        props.disabled && "cursor-not-allowed opacity-50",
        className
      )}
    >
      <span className="relative inline-flex h-4 w-4 shrink-0">
        <input
          type="checkbox"
          className="peer absolute inset-0 h-full w-full cursor-pointer opacity-0"
          {...props}
        />
        <span className="pointer-events-none flex h-full w-full items-center justify-center rounded border border-line-3 bg-panel-1 text-transparent transition-all duration-150 peer-checked:border-accent peer-checked:bg-accent peer-checked:text-white peer-focus-visible:outline-2 peer-focus-visible:outline-accent">
          <Check className="h-3 w-3" strokeWidth={3} />
        </span>
      </span>
      {label && <span className="text-sm text-ink-2 group-hover:text-ink">{label}</span>}
    </label>
  );
}
