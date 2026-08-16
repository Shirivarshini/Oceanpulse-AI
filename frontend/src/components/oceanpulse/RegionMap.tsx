import { useState } from "react";
import { Dna, Ship, Radar } from "lucide-react";
import { cn } from "@/lib/utils";
import { LEVEL_STYLES } from "@/lib/oceanpulse/config";
import type { AnalysisResult, MapMarker } from "@/lib/oceanpulse/types";
import { DataSourceLabel } from "./DataSourceLabel";
import { Skeleton } from "./LoadingState";

const LAYERS = ["Ocean", "Fisheries", "Species", "eDNA"] as const;
type Layer = (typeof LAYERS)[number];

const MARKER_COLORS: Record<MapMarker["severity"], string> = {
  low: "var(--accent)",
  moderate: "var(--signal-watch)",
  high: "var(--signal-stressed)",
  severe: "var(--critical)",
};

const W = 720;
const H = 420;

function markerVisible(marker: MapMarker, layers: Layer[]) {
  if (marker.kind === "vessel") return layers.includes("Fisheries");
  if (marker.kind === "edna") return layers.includes("eDNA");
  return layers.includes("Species") || layers.includes("Ocean");
}

export function RegionMap({
  result,
  loading,
}: {
  result: AnalysisResult | null;
  loading: boolean;
}) {
  const [layers, setLayers] = useState<Layer[]>([...LAYERS]);

  if (loading || !result) {
    return (
      <div className="panel p-5">
        <Skeleton className="h-[420px] w-full" />
      </div>
    );
  }

  /*
   * The current Backend Region response uses:
   *
   *   latitude
   *   longitude
   *
   * rather than:
   *
   *   center.lat
   *   center.lon
   *
   * Build the map bounds locally from the Backend coordinates.
   */
  const latitude = result.region.latitude;
  const longitude = result.region.longitude;

  const minLon = longitude - 0.5;
  const minLat = latitude - 0.5;
  const maxLon = longitude + 0.5;
  const maxLat = latitude + 0.5;

  const project = (lat: number, lon: number) => ({
    x: ((lon - minLon) / (maxLon - minLon)) * W,
    y: H - ((lat - minLat) / (maxLat - minLat)) * H,
  });

  const style = LEVEL_STYLES[result.level];

  return (
    <section className="panel overflow-hidden">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline px-5 py-4">
        <div>
          <h2 className="font-display text-sm font-medium tracking-wide text-foreground">
            {result.region.name}
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            Gulf of Mannar &middot; {latitude.toFixed(2)}°N{" "}
            {longitude.toFixed(2)}°E
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {LAYERS.map((layer) => {
            const active = layers.includes(layer);

            return (
              <button
                key={layer}
                type="button"
                aria-pressed={active}
                onClick={() =>
                  setLayers((prev) =>
                    prev.includes(layer)
                      ? prev.filter((l) => l !== layer)
                      : [...prev, layer],
                  )
                }
                className={cn(
                  "rounded-full border px-3 py-1 text-[11px] tracking-wide transition-colors",
                  active
                    ? "border-accent/50 bg-accent/10 text-accent"
                    : "border-hairline text-muted-foreground hover:text-body",
                )}
              >
                {layer}
              </button>
            );
          })}

          <DataSourceLabel status={result.source} />
        </div>
      </header>

      <div className="relative">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="grid-ocean h-[420px] w-full bg-background"
          role="img"
          aria-label={`Deterministic marine map of ${result.region.name}`}
        >
          {layers.includes("Ocean") && (
            <>
              <path
                d={`M0,${H * 0.18} C ${W * 0.2},${H * 0.3} ${W * 0.35
                  },${H * 0.12} ${W * 0.55},${H * 0.24} S ${W * 0.85
                  },${H * 0.4} ${W},${H * 0.3} L ${W},0 L 0,0 Z`}
                fill="var(--elevated)"
                stroke="var(--hairline-strong)"
              />

              <path
                d={`M0,${H * 0.3} C ${W * 0.25},${H * 0.42} ${W * 0.45
                  },${H * 0.26} ${W * 0.7},${H * 0.38} S ${W * 0.9
                  },${H * 0.5} ${W},${H * 0.44}`}
                fill="none"
                stroke="var(--accent)"
                strokeOpacity={0.25}
                strokeDasharray="6 6"
              />
            </>
          )}

          <ellipse
            cx={W / 2}
            cy={H * 0.62}
            rx={W * 0.32}
            ry={H * 0.26}
            fill="var(--accent)"
            fillOpacity={result.index >= 80 ? 0.05 : 0.08}
            stroke="var(--accent)"
            strokeOpacity={0.35}
            strokeDasharray="3 5"
          />

          <ellipse
            cx={W / 2}
            cy={H * 0.62}
            rx={W * 0.2}
            ry={H * 0.16}
            fill={
              result.index >= 60
                ? "var(--critical)"
                : "var(--accent)"
            }
            fillOpacity={0.12}
            stroke={
              result.index >= 60
                ? "var(--critical)"
                : "var(--accent)"
            }
            strokeOpacity={0.45}
          />

          {(result.markers ?? [])
            .filter((marker) => markerVisible(marker, layers))
            .map((marker) => {
              const { x, y } = project(marker.lat, marker.lon);
              const color = MARKER_COLORS[marker.severity];

              return (
                <g key={marker.id}>
                  <circle
                    cx={x}
                    cy={y}
                    r={12}
                    fill={color}
                    fillOpacity={0.14}
                  />

                  <circle
                    cx={x}
                    cy={y}
                    r={4}
                    fill={color}
                  />

                  <text
                    x={x + 12}
                    y={y + 4}
                    fill="var(--muted-foreground)"
                    fontSize={11}
                    fontFamily="Inter, sans-serif"
                  >
                    {marker.label}
                  </text>
                </g>
              );
            })}
        </svg>

        <div className="absolute bottom-4 left-4 flex items-center gap-4 rounded-[10px] border border-hairline bg-surface/90 px-3 py-2 text-[11px] text-muted-foreground backdrop-blur">
          <span className="flex items-center gap-1.5">
            <Radar className="size-3.5 text-accent" />
            Station
          </span>

          <span className="flex items-center gap-1.5">
            <Ship className="size-3.5 text-signal-watch" />
            Vessel
          </span>

          <span className="flex items-center gap-1.5">
            <Dna className="size-3.5 text-signal-stressed" />
            eDNA
          </span>
        </div>

        <div
          className={cn(
            "absolute top-4 right-4 rounded-full border px-3 py-1 text-[11px] tracking-[0.12em]",
            style.border,
            style.bg,
            style.text,
          )}
        >
          {result.level} &middot; {result.index}
        </div>
      </div>
    </section>
  );
}