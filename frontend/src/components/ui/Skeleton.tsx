import { cn } from "../../lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn("skeleton rounded-lg", className)} />;
}

export function SkeletonLines({ lines, className }: { lines?: number; className?: string }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines ?? 3 }).map((_, i) => (
        <Skeleton key={i} className={cn("h-3 w-full", i === (lines ?? 3) - 1 && "w-2/3", className)} />
      ))}
    </div>
  );
}
