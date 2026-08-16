import { Activity, CalendarRange, Loader2 } from "lucide-react";
import { PERIODS } from "@/lib/oceanpulse/config";
import type { Region, ScenarioId } from "@/lib/oceanpulse/types";
import { RegionSelector } from "./RegionSelector";
import { ScenarioSelector } from "./ScenarioSelector";

export function ControlBar({
  regions,
  regionId,
  scenario,
  period,
  loading,
  onRegionChange,
  onScenarioChange,
  onPeriodChange,
  onRun,
}: {
  regions: Region[];
  regionId: string;
  scenario: ScenarioId;
  period: string;
  loading: boolean;
  onRegionChange: (id: string) => void;
  onScenarioChange: (id: ScenarioId) => void;
  onPeriodChange: (period: string) => void;
  onRun: () => void;
}) {
  return (
    <section className="tile p-5">
      <div className="mb-4 flex items-center gap-3 border-b border-hairline pb-4">
        <span className="label-caps text-accent">Query Console</span>
        <span className="h-px flex-1 bg-hairline" aria-hidden />
        <span className="text-[10px] tracking-[0.16em] text-muted-foreground">
          {loading ? "REQUEST IN FLIGHT" : "READY"}
        </span>
      </div>

      <div className="grid gap-5 xl:grid-cols-[240px_minmax(0,1fr)_190px_auto] xl:items-end">
        <RegionSelector regions={regions} value={regionId} onChange={onRegionChange} />
        <ScenarioSelector value={scenario} onChange={onScenarioChange} />

        <label className="block">
          <span className="label-caps">Period</span>
          <div className="mt-2 flex items-center gap-2 rounded-full border border-hairline bg-elevated px-4 py-2.5">
            <CalendarRange className="size-4 shrink-0 text-accent" />
            <select
              value={period}
              onChange={(e) => onPeriodChange(e.target.value)}
              className="w-full bg-transparent text-sm text-body outline-none"
            >
              {PERIODS.map((p) => (
                <option key={p} value={p} className="bg-elevated text-body">
                  {p}
                </option>
              ))}
            </select>
          </div>
        </label>

        <button
          onClick={onRun}
          disabled={loading}
          className="inline-flex h-[44px] w-full items-center justify-center gap-2 rounded-full bg-primary px-6 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60 xl:w-auto"
        >
          {loading ? (
            <>
              <Loader2 className="size-4 animate-spin" /> Running analysis...
            </>
          ) : (
            <>
              <Activity className="size-4" /> Run Analysis
            </>
          )}
        </button>
      </div>
    </section>
  );
}
