import type { SpeciesMatch, SourceStatus } from "@/lib/oceanpulse/types";
import { DataSourceLabel } from "./DataSourceLabel";
import { Panel } from "./Panel";
import { SpeciesMatchCard } from "./SpeciesMatchCard";
import { Skeleton } from "./LoadingState";

export function MolecularBiodiversity({
  species,
  source,
  loading,
}: {
  species: SpeciesMatch[];
  source: SourceStatus;
  loading: boolean;
}) {
  return (
    <Panel
      title="Molecular Biodiversity"
      subtitle="Confidence-scored eDNA signals from the selected region."
      right={<DataSourceLabel status={source} />}
    >
      {loading ? (
        <div className="grid gap-4 md:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            {species.map((m) => (
              <SpeciesMatchCard key={m.sample_id} match={m} />
            ))}
          </div>
          <p className="mt-4 text-[11px] text-muted-foreground">
            DEMO taxonomic matches shown for demonstration only — not confirmed scientific findings.
          </p>
        </>
      )}
    </Panel>
  );
}
