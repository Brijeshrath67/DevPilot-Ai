import { Circle, Loader2 } from "lucide-react";
import { Badge, type BadgeTone } from "../ui/Badge";
import { cn } from "../../lib/utils";

const STATUS_CONFIG: Record<
  string,
  { tone: BadgeTone; label: string; pulse?: boolean; spinner?: boolean }
> = {
  pending: { tone: "warning", label: "pending", pulse: true },
  analyzing: { tone: "accent", label: "analyzing", spinner: true },
  analyzed: { tone: "success", label: "analyzed" },
  error: { tone: "critical", label: "error" },
};

export interface RepoStatusBadgeProps {
  status?: string | null;
  className?: string;
}

export function RepoStatusBadge({ status, className }: RepoStatusBadgeProps) {
  const config = STATUS_CONFIG[status ?? ""] ?? { tone: "neutral" as BadgeTone, label: status ?? "unknown" };

  return (
    <Badge tone={config.tone} className={className}>
      {config.spinner ? (
        <Loader2 className="h-2.5 w-2.5 animate-spin" aria-hidden />
      ) : config.pulse ? (
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-60" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-current" />
        </span>
      ) : (
        <Circle className="h-1.5 w-1.5 fill-current" aria-hidden />
      )}
      <span className={cn("capitalize", config.spinner && "animate-pulse-glow")}>{config.label}</span>
    </Badge>
  );
}
