import { useEffect, useState } from "react";
import { cn, scoreColor } from "../../lib/utils";

export interface ScoreBarProps {
  label: string;
  value: number;
  className?: string;
}

export function ScoreBar({ label, value, className }: ScoreBarProps) {
  const [width, setWidth] = useState(0);
  const clamped = Math.max(0, Math.min(100, value));
  const color = scoreColor(clamped);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setWidth(clamped));
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="flex items-baseline justify-between">
        <span className="text-xs font-medium text-ink-2">{label}</span>
        <span className="font-mono text-sm font-semibold tabular-nums" style={{ color }}>
          {Math.round(value)}
        </span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-panel-3">
        <div
          className="h-full rounded-full transition-[width] duration-700 ease-out"
          style={{ width: `${width}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
