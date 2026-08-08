import { Lightbulb } from "lucide-react";
import { cn } from "../../lib/utils";

export interface RecommendationsListProps {
  recommendations: string[];
  className?: string;
}

export function RecommendationsList({ recommendations, className }: RecommendationsListProps) {
  if (recommendations.length === 0) return null;
  return (
    <div className={cn("rounded-xl border border-line-1 bg-panel-2 p-4", className)}>
      <div className="mb-2.5 flex items-center gap-2">
        <Lightbulb className="h-3.5 w-3.5 text-accent" />
        <h3 className="text-xs font-semibold uppercase tracking-[0.08em] text-ink-2">Recommendations</h3>
      </div>
      <ul className="space-y-1.5">
        {recommendations.map((rec, index) => (
          <li key={index} className="flex gap-2 text-[13px] leading-relaxed text-ink-2">
            <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-accent" />
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
