import { FactorRow } from "./FactorRow";
import { DataSourceLabel } from "./DataSourceLabel";
import { Panel } from "./Panel";
import { Skeleton } from "./LoadingState";
import type {
  ContributingFactor,
  SourceStatus,
} from "@/lib/oceanpulse/types";

interface ContributingFactorsProps {
  factors: ContributingFactor[];
  source: SourceStatus;
  loading: boolean;
}

export function ContributingFactors({
  factors,
  source,
  loading,
}: ContributingFactorsProps) {
  if (loading) {
    return (
      <Panel
        title="Contributing Factors"
        subtitle="Signals contributing to the current ecosystem index."
      >
        <div className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      </Panel>
    );
  }

  return (
    <Panel
      title="Contributing Factors"
      subtitle="Signals contributing to the current ecosystem index."
      right={<DataSourceLabel status={source} />}
    >
      {factors.length === 0 ? (
        <div className="py-8 text-center text-sm text-muted-foreground">
          No contributing factors available.
        </div>
      ) : (
        <div>
          {factors.map((factor, index) => (
            <FactorRow
              key={`${factor.key}-${factor.name}-${index}`}
              factor={factor}
            />
          ))}
        </div>
      )}
    </Panel>
  );
}