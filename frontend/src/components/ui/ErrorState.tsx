import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";
import { cn } from "../../lib/utils";

export interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({ message, onRetry, className }: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        "flex items-center justify-between gap-4 rounded-lg border border-critical/25 bg-critical/5 px-4 py-3",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-critical" aria-hidden />
        <div className="space-y-0.5">
          <p className="text-sm font-medium text-critical">{message || "Something went wrong."}</p>
          {onRetry && <p className="text-xs text-ink-3">The operation did not complete.</p>}
        </div>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} icon={<RefreshCw className="h-3.5 w-3.5" />}>
          Retry
        </Button>
      )}
    </div>
  );
}
