import { Clock3 } from "lucide-react";
import { cn } from "@/lib/utils";
import { LEVEL_STYLES } from "@/lib/oceanpulse/config";
import type { IndexLevel, TimelinePoint } from "@/lib/oceanpulse/types";
import { Skeleton } from "./LoadingState";

const FALLBACK_LEVEL: IndexLevel = "STABLE";

function getLevelStyle(level: unknown) {
  if (
    level === "STABLE" ||
    level === "WATCH" ||
    level === "STRESSED" ||
    level === "CRITICAL"
  ) {
    return LEVEL_STYLES[level];
  }

  return LEVEL_STYLES[FALLBACK_LEVEL];
}

function getSafeLevel(level: unknown): IndexLevel {
  if (
    level === "STABLE" ||
    level === "WATCH" ||
    level === "STRESSED" ||
    level === "CRITICAL"
  ) {
    return level;
  }

  return FALLBACK_LEVEL;
}

export function Timeline({
  timeline,
  loading,
}: {
  timeline: TimelinePoint[] | null;
  loading: boolean;
}) {
  if (loading || !timeline) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (timeline.length === 0) {
    return (
      <section className="tile">
        <header className="flex items-center gap-2 border-b border-hairline px-5 py-4">
          <Clock3 className="size-4 text-accent" />
          <h2 className="font-display text-sm font-medium tracking-wide text-foreground">
            Timeline
          </h2>
        </header>

        <div className="px-5 py-8 text-center text-sm text-muted-foreground">
          No timeline data available.
        </div>
      </section>
    );
  }

  return (
    <section className="tile">
      <header className="flex items-center gap-2 border-b border-hairline px-5 py-4">
        <Clock3 className="size-4 text-accent" />
        <h2 className="font-display text-sm font-medium tracking-wide text-foreground">
          Timeline
        </h2>
      </header>

      <div className="relative px-5 py-5">
        <div className="absolute bottom-5 left-[34px] top-5 w-px bg-hairline" />

        <div className="space-y-0">
          {timeline.map((point, index) => {
            const safeLevel = getSafeLevel(point.level);
            const style = getLevelStyle(point.level);

            return (
              <div
                key={`${point.day}-${point.label}-${index}`}
                className="relative grid grid-cols-[20px_minmax(0,1fr)] gap-4 py-3 first:pt-0 last:pb-0"
              >
                <div className="relative z-10 flex items-start justify-center">
                  <span
                    className={cn(
                      "mt-1.5 size-2.5 rounded-full ring-4 ring-surface",
                      style.dot,
                    )}
                    aria-label={safeLevel}
                  />
                </div>

                <div className="min-w-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <div className="flex items-baseline gap-2">
                      <p className="text-sm font-medium text-foreground">
                        {point.label}
                      </p>

                      <span
                        className={cn(
                          "text-[10px] font-medium tracking-[0.1em]",
                          style.text,
                        )}
                      >
                        {safeLevel}
                      </span>
                    </div>

                    <span className="label-caps shrink-0">
                      Day {point.day}
                    </span>
                  </div>

                  <div className="mt-1 flex flex-wrap items-center gap-3">
                    <span className="font-display text-lg tabular-nums text-body">
                      {point.index}
                    </span>

                    {point.event && (
                      <span className="text-xs text-muted-foreground">
                        {point.event}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}