import { cn } from "@/lib/utils";
import type { SourceStatus } from "@/lib/oceanpulse/types";

const STYLES: Record<SourceStatus, string> = {
  LIVE: "text-accent border-accent/40",
  CACHED: "text-signal-watch border-signal-watch/40",
  HISTORICAL: "text-muted-foreground border-hairline-strong",
  DEMO: "text-muted-foreground border-hairline-strong",
};

export function DataSourceLabel({
  status,
  className,
}: {
  status: SourceStatus;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border bg-elevated/60 px-2.5 py-0.5 text-[10px] font-medium tracking-[0.14em]",
        STYLES[status],
        className,
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}
