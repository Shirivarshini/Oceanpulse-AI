import { Fish, Ship, Thermometer, Dna } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  ContributingFactor,
  FactorKey,
  FactorSeverity,
} from "@/lib/oceanpulse/types";

const ICONS: Record<FactorKey, typeof Fish> = {
  ocean_temperature: Thermometer,
  fisheries_pressure: Fish,
  biodiversity: Dna,
  vessel_activity: Ship,
};

const SEVERITY: Record<
  FactorSeverity,
  { text: string; bar: string }
> = {
  low: {
    text: "text-accent",
    bar: "bg-accent",
  },
  moderate: {
    text: "text-signal-watch",
    bar: "bg-signal-watch",
  },
  high: {
    text: "text-signal-stressed",
    bar: "bg-signal-stressed",
  },
  severe: {
    text: "text-critical",
    bar: "bg-critical",
  },
};

export function FactorRow({
  factor,
}: {
  factor: ContributingFactor;
}) {
  // Runtime-safe icon lookup.
  // Prevents React from attempting to render an undefined component
  // if the backend sends an unexpected factor key.
  const Icon = ICONS[factor.key] ?? Fish;

  // Runtime-safe severity lookup.
  const severity =
    SEVERITY[factor.severity] ?? SEVERITY.moderate;

  // Ensure impact is a valid number.
  const impact =
    typeof factor.impact === "number" && Number.isFinite(factor.impact)
      ? factor.impact
      : 0;

  // Keep the progress bar between 0% and 100%.
  const width = Math.min(
    100,
    Math.max(0, (impact / 35) * 100),
  );

  return (
    <div className="border-b border-hairline py-3 last:border-b-0">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-[10px] border border-hairline bg-elevated">
          <Icon
            className={cn(
              "size-4",
              severity.text,
            )}
          />
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-3">
            <p className="text-sm text-foreground">
              {factor.name}
            </p>

            <p
              className={cn(
                "font-display text-sm tabular-nums",
                severity.text,
              )}
            >
              +{impact} impact
            </p>
          </div>

          <p className="mt-0.5 text-xs text-muted-foreground">
            {factor.explanation}
          </p>

          <div className="mt-2 flex items-center gap-3">
            <div className="h-1 flex-1 overflow-hidden rounded-full bg-elevated">
              <div
                className={cn(
                  "h-full rounded-full transition-[width] duration-700",
                  severity.bar,
                )}
                style={{
                  width: `${width}%`,
                }}
              />
            </div>

            <span className="label-caps shrink-0">
              {factor.severity}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}