import { Waves, Fish, Dna, Radar } from "lucide-react";
import type { DataSource } from "@/lib/oceanpulse/types";
import { DataSourceLabel } from "./DataSourceLabel";
import { Panel } from "./Panel";
import { Skeleton } from "./LoadingState";

const ICONS = [Waves, Fish, Dna, Radar];

export function DataSources({
  sources,
  loading = false,
}: {
  sources: DataSource[];
  loading?: boolean;
}) {
  return (
    <Panel
      title="Signal Provenance"
      subtitle="Status reported by the analysis service for every fused signal."
      bodyClassName="space-y-2"
    >
      {loading
        ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)
        : sources.map((s, i) => {
            const Icon = ICONS[i % ICONS.length]!;
            return (
              <div
                key={s.id}
                className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-[10px] border border-hairline bg-elevated/40 px-3 py-2.5"
              >
                <span className="flex size-8 shrink-0 items-center justify-center rounded-[10px] border border-hairline bg-surface">
                  <Icon className="size-4 text-accent" />
                </span>
                <div className="min-w-0">
                  <p className="truncate text-sm text-foreground">{s.name}</p>
                  <p className="mt-0.5 truncate text-xs text-muted-foreground">{s.detail}</p>
                </div>
                <DataSourceLabel status={s.status} />
              </div>
            );
          })}
    </Panel>
  );
}
