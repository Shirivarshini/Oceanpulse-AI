import type { Analysis } from "@/lib/oceanpulse/types";
import { SourceLabel } from "./SourceLabel";

/**
 * Task 2 shell: static bathymetric placeholder with the region marker.
 * Task 4 swaps the inner surface for the Leaflet map (client-only import).
 */
export function RegionMapPanel({ analysis }: { analysis: Analysis }) {
  const critical = analysis.level === "CRITICAL" || analysis.level === "STRESSED";

  return (
    <section className="overflow-hidden rounded-[10px] bg-trench">
      <div className="relative h-72 bg-deep-water">
        <div
          aria-hidden
          className="absolute inset-0 opacity-60"
          style={{
            backgroundImage:
              "linear-gradient(#1a2530 1px, transparent 1px), linear-gradient(90deg, #1a2530 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="relative flex items-center justify-center">
            <span
              className={`live-pulse absolute size-16 rounded-full ${critical ? "bg-coral-alert/15" : "bg-bioluminescence/15"}`}
            />
            <span
              className={`size-3 rounded-full ${critical ? "bg-coral-alert" : "bg-bioluminescence"}`}
            />
          </span>
        </div>
        <div className="absolute bottom-3 left-4 text-[13px] text-sea-fog">
          {analysis.region.name} · {analysis.region.latitude.toFixed(2)},{" "}
          {analysis.region.longitude.toFixed(2)}
        </div>
      </div>
      <div className="flex items-center justify-between gap-3 px-5 py-3">
        <p className="text-[13px] text-slate-tide">Region map · interactive layer pending</p>
        <SourceLabel source={analysis.sources.ocean} />
      </div>
    </section>
  );
}
