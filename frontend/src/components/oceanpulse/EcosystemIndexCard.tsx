import type { Analysis } from "@/lib/oceanpulse/types";
import { LevelBadge } from "./LevelBadge";
import { SourceLabel } from "./SourceLabel";
import { TrendChart } from "./TrendChart";

export function EcosystemIndexCard({ analysis }: { analysis: Analysis }) {
  return (
    <section className="rounded-[10px] bg-trench p-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-[24px] leading-none text-surf-white">{analysis.region.name}</h2>
          <p className="mt-1.5 text-[13px] text-sea-fog">
            {analysis.region.latitude.toFixed(2)}°N, {analysis.region.longitude.toFixed(2)}°E
          </p>
        </div>
        <LevelBadge level={analysis.level} />
      </header>

      <div className="mt-8 flex flex-wrap items-end gap-6">
        <p className="font-display text-[64px] leading-none text-surf-white">{analysis.index}</p>
        <div className="pb-2">
          <p className="text-[13px] tracking-wide text-sea-fog uppercase">Ecosystem index</p>
          <p className="mt-1 text-[15px] text-shell">
            Confidence {Math.round(analysis.confidence * 100)}%
          </p>
        </div>
      </div>

      <div className="mt-6">
        <TrendChart timeline={analysis.timeline} />
      </div>

      <footer className="mt-5 flex flex-wrap gap-2 border-t border-reef-shadow pt-4">
        <SourceLabel prefix="Ocean" source={analysis.sources.ocean} />
        <SourceLabel prefix="Fisheries" source={analysis.sources.fisheries} />
        <SourceLabel prefix="Molecular" source={analysis.sources.molecular} />
      </footer>
    </section>
  );
}
