import { cn } from "@/lib/utils";
import type { SpeciesMatch } from "@/lib/oceanpulse/types";
import { ConfidenceBar } from "./ConfidenceBar";
import { DataSourceLabel } from "./DataSourceLabel";

const STATUS: Record<SpeciesMatch["status"], string> = {
  common: "text-accent border-accent/40",
  rare: "text-signal-watch border-signal-watch/40",
  invasive: "text-critical border-critical/40",
};

export function SpeciesMatchCard({ match }: { match: SpeciesMatch }) {
  return (
    <article className="panel flex flex-col gap-4 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-base text-foreground italic">{match.taxon}</h3>
          <p className="mt-0.5 text-[11px] text-muted-foreground">Sample {match.sample_id}</p>
        </div>
        <span
          className={cn(
            "rounded-full border px-2.5 py-0.5 text-[10px] tracking-[0.12em]",
            STATUS[match.status],
          )}
        >
          {match.status.toUpperCase()}
        </span>
      </div>

      <ConfidenceBar value={match.confidence} label="Match confidence" />

      <dl className="grid grid-cols-2 gap-y-2 border-t border-hairline pt-3 text-[11px]">
        <dt className="text-muted-foreground">Sample date</dt>
        <dd className="text-right text-body">{match.sample_date}</dd>
        <dt className="text-muted-foreground">Reference</dt>
        <dd className="text-right text-body">{match.reference}</dd>
      </dl>

      <DataSourceLabel status={match.source} className="self-start" />
    </article>
  );
}
