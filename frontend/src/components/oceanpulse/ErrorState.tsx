import { AlertTriangle, RefreshCw } from "lucide-react";

export function ErrorState({
  title = "Analysis unavailable.",
  message = "Using DEMO data. Results are simulated and not live observations.",
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex items-start gap-3 rounded-[10px] border border-critical/40 bg-critical/10 px-4 py-3">
      <AlertTriangle className="mt-0.5 size-4 shrink-0 text-critical" />
      <div className="flex-1">
        <p className="text-sm font-medium text-foreground">{title}</p>
        <p className="mt-1 text-xs text-muted-foreground">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 rounded-full border border-hairline-strong px-3 py-1 text-xs text-body transition-colors hover:bg-elevated"
        >
          <RefreshCw className="size-3" /> Retry
        </button>
      )}
    </div>
  );
}
