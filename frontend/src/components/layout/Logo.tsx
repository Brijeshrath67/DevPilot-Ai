import { cn } from "../../lib/utils";

export function Logo({ size = 28, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden
      className={cn("shrink-0", className)}
    >
      <rect x="1" y="1" width="30" height="30" rx="8" fill="var(--accent)" fillOpacity="0.12" stroke="var(--accent)" strokeOpacity="0.4" />
      <path
        d="M10 11l5 5-5 5M22 11l-5 5 5 5"
        stroke="var(--accent)"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="24.5" cy="7.5" r="2" fill="var(--accent-2)" />
    </svg>
  );
}
