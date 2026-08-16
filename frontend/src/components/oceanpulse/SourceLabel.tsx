import type { DataSource } from "@/lib/oceanpulse/types";
import { cn } from "@/lib/utils";

const TONE: Record<DataSource, string> = {
  LIVE: "border-bioluminescence text-bioluminescence",
  CACHED: "border-tide-current text-sea-fog",
  HISTORICAL: "border-tide-current text-sea-fog",
  DEMO: "border-tide-current text-slate-tide",
};

/** Provenance is never hidden — every data-derived element carries one. */
export function SourceLabel({
  source,
  prefix,
  className,
}: {
  source: DataSource;
  prefix?: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[12px] font-medium tracking-wide uppercase",
        TONE[source],
        className,
      )}
    >
      {source === "LIVE" && (
        <span className="live-pulse size-1.5 rounded-full bg-bioluminescence" />
      )}
      {prefix ? `${prefix} · ` : ""}
      {source}
    </span>
  );
}
