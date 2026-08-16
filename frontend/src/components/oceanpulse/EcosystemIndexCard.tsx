import { cn } from "@/lib/utils";
import { LEVEL_STYLES } from "@/lib/oceanpulse/config";
import type { AnalysisResult } from "@/lib/oceanpulse/types";
import { ConfidenceBar } from "./ConfidenceBar";
import { DataSourceLabel } from "./DataSourceLabel";
import { IndexGauge } from "./IndexGauge";
import { Skeleton } from "./LoadingState";

const LEVELS = ["STABLE", "WATCH", "STRESSED", "CRITICAL"] as const;

export function EcosystemIndexCard({
  result,
  loading,
}: {
  result: AnalysisResult | null;
  loading: boolean;
}) {
  if (loading || !result) {
    return (
      <div className="tile flex flex-col gap-6 p-6">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="mx-auto h-[240px] w-[240px] rounded-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  const style = LEVEL_STYLES[result.level];

  return (
    <section className="tile flex flex-col gap-5 p-6">
      <div className="dial-glow pointer-events-none absolute inset-x-0 top-6 h-72" aria-hidden />

      <header className="relative grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
        <div className="min-w-0">
          <p className="label-caps text-accent">Ecosystem Index</p>
          <p className="mt-1 truncate text-xs text-muted-foreground">
            {result.region.name} &middot; {result.period}
          </p>
        </div>
        <DataSourceLabel status={result.source} />
      </header>

      <div className="relative">
        <IndexGauge index={result.index} level={result.level} />
      </div>

      <div className="relative flex flex-wrap items-center justify-center gap-3">
        <span
          className={cn(
            "inline-flex items-center gap-2 rounded-full border px-3.5 py-1 text-xs font-medium tracking-[0.14em]",
            style.border,
            style.bg,
            style.text,
          )}
        >
          <span className={cn("size-1.5 rounded-full", style.dot)} />
          {result.level}
        </span>
        <span className="text-xs text-muted-foreground">
          {Math.round(result.confidence * 100)}% confidence
        </span>
      </div>

      <ConfidenceBar value={result.confidence} label="Fusion confidence" />

      <div className="relative grid grid-cols-4 gap-1 border-t border-hairline pt-4 text-[10px] tracking-[0.1em] text-muted-foreground">
        {LEVELS.map((lvl) => (
          <span
            key={lvl}
            className={cn(
              "text-center",
              lvl === result.level ? LEVEL_STYLES[lvl].text : "opacity-40",
            )}
          >
            {lvl}
          </span>
        ))}
      </div>
    </section>
  );
}
