import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { Dna, Fish, Ship, Thermometer } from "lucide-react";
import { cn } from "@/lib/utils";
import { LEVEL_STYLES } from "@/lib/oceanpulse/config";
import type {
  AnalysisResult,
  MapMarker,
  ScenarioId,
} from "@/lib/oceanpulse/types";
import { DataSourceLabel } from "./DataSourceLabel";
import { Skeleton } from "./LoadingState";

import "leaflet/dist/leaflet.css";

const LAYERS = ["Ocean", "Fisheries", "Species", "eDNA"] as const;
type Layer = (typeof LAYERS)[number];

const MARKER_COLORS: Record<MapMarker["severity"], string> = {
  low: "#38bdf8",
  moderate: "#facc15",
  high: "#fb923c",
  severe: "#ef4444",
};

const SCENARIO_CONFIG: Record<
  ScenarioId,
  {
    zoom: number;
    label: string;
    description: string;
    accent: string;
  }
> = {
  healthy_reef: {
    zoom: 8,
    label: "REEF BASELINE",
    description: "Stable reef monitoring zone",
    accent: "#38bdf8",
  },
  declining_fishery: {
    zoom: 9,
    label: "FISHERY PRESSURE",
    description: "Vessel activity and fisheries monitoring",
    accent: "#facc15",
  },
  coral_bleaching: {
    zoom: 10,
    label: "THERMAL STRESS",
    description: "Coral bleaching impact zone",
    accent: "#ef4444",
  },
};

function markerVisible(marker: MapMarker, layers: Layer[]) {
  if (marker.kind === "vessel") {
    return layers.includes("Fisheries");
  }

  if (marker.kind === "edna") {
    return layers.includes("eDNA");
  }

  return layers.includes("Species") || layers.includes("Ocean");
}

function scenarioMarkers(
  scenario: ScenarioId,
  latitude: number,
  longitude: number,
  level: AnalysisResult["level"],
): MapMarker[] {
  if (scenario === "healthy_reef") {
    return [
      {
        id: "healthy-station-01",
        kind: "station",
        label: "Reef Monitoring Station",
        lat: latitude + 0.13,
        lon: longitude - 0.17,
        severity: "low",
      },
      {
        id: "healthy-station-02",
        kind: "station",
        label: "Ocean Observation Station",
        lat: latitude - 0.11,
        lon: longitude + 0.18,
        severity: "low",
      },
      {
        id: "healthy-edna-01",
        kind: "edna",
        label: "Healthy eDNA Sample",
        lat: latitude + 0.02,
        lon: longitude + 0.11,
        severity: "low",
      },
      {
        id: "healthy-vessel-01",
        kind: "vessel",
        label: "Normal Vessel Activity",
        lat: latitude - 0.19,
        lon: longitude - 0.06,
        severity: "low",
      },
    ];
  }

  if (scenario === "declining_fishery") {
    return [
      {
        id: "fishery-vessel-01",
        kind: "vessel",
        label: "Fishing Activity",
        lat: latitude + 0.08,
        lon: longitude - 0.22,
        severity: "high",
      },
      {
        id: "fishery-vessel-02",
        kind: "vessel",
        label: "Fishing Vessel",
        lat: latitude - 0.05,
        lon: longitude + 0.19,
        severity: "high",
      },
      {
        id: "fishery-vessel-03",
        kind: "vessel",
        label: "Elevated Vessel Activity",
        lat: latitude - 0.18,
        lon: longitude + 0.04,
        severity: "moderate",
      },
      {
        id: "fishery-station-01",
        kind: "station",
        label: "Fisheries Monitoring Station",
        lat: latitude + 0.18,
        lon: longitude + 0.08,
        severity: "moderate",
      },
      {
        id: "fishery-edna-01",
        kind: "edna",
        label: "Biodiversity Sample",
        lat: latitude - 0.02,
        lon: longitude - 0.31,
        severity: "moderate",
      },
    ];
  }

  return [
    {
      id: "bleaching-station-01",
      kind: "station",
      label: "Thermal Stress Station",
      lat: latitude + 0.13,
      lon: longitude - 0.13,
      severity: "severe",
    },
    {
      id: "bleaching-station-02",
      kind: "station",
      label: "Coral Monitoring Station",
      lat: latitude - 0.10,
      lon: longitude + 0.15,
      severity: "high",
    },
    {
      id: "bleaching-edna-01",
      kind: "edna",
      label: "eDNA Biodiversity Sample",
      lat: latitude + 0.01,
      lon: longitude + 0.03,
      severity: "high",
    },
    {
      id: "bleaching-edna-02",
      kind: "edna",
      label: "eDNA Stress Sample",
      lat: latitude - 0.16,
      lon: longitude - 0.20,
      severity: "severe",
    },
    {
      id: "bleaching-vessel-01",
      kind: "vessel",
      label: "Vessel Activity",
      lat: latitude + 0.25,
      lon: longitude + 0.22,
      severity: level === "CRITICAL" ? "high" : "moderate",
    },
  ];
}

/*
 * Leaflet is browser-only.
 *
 * We deliberately load react-leaflet dynamically so TanStack Start/Nitro
 * does not attempt to execute Leaflet during SSR where `window` does not exist.
 */
const LeafletMap = lazy(async () => {
  const leaflet = await import("react-leaflet");

  function ClientMap({
    latitude,
    longitude,
    zoom,
    scenario,
    result,
    layers,
    markers,
    config,
    impactRadius,
    impactColor,
  }: {
    latitude: number;
    longitude: number;
    zoom: number;
    scenario: ScenarioId;
    result: AnalysisResult;
    layers: Layer[];
    markers: MapMarker[];
    config: (typeof SCENARIO_CONFIG)[ScenarioId];
    impactRadius: number;
    impactColor: string;
  }) {
    const {
      MapContainer,
      TileLayer,
      Circle,
      CircleMarker,
      Polygon,
      Popup,
      useMap,
    } = leaflet;

    function MapViewport() {
      const map = useMap();

      useEffect(() => {
        map.setView([latitude, longitude], zoom, {
          animate: true,
          duration: 0.7,
        });
      }, [map, latitude, longitude, zoom]);

      return null;
    }

    return (
      <MapContainer
        center={[latitude, longitude]}
        zoom={zoom}
        scrollWheelZoom
        className="h-[420px] w-full bg-background"
        zoomControl
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapViewport />

        {layers.includes("Ocean") && (
          <Circle
            center={[latitude, longitude]}
            radius={impactRadius * 1000}
            pathOptions={{
              color: impactColor,
              weight: 2,
              opacity: 0.55,
              fillColor: impactColor,
              fillOpacity:
                scenario === "coral_bleaching"
                  ? 0.16
                  : scenario === "declining_fishery"
                    ? 0.11
                    : 0.07,
              dashArray: scenario === "healthy_reef" ? "8 8" : "5 5",
            }}
          >
            <Popup>
              <strong>{config.label}</strong>
              <br />
              {config.description}
              <br />
              Ecosystem Index: {result.index}
            </Popup>
          </Circle>
        )}

        {scenario === "coral_bleaching" && layers.includes("Ocean") && (
          <Circle
            center={[latitude + 0.01, longitude - 0.02]}
            radius={14 * 1000}
            pathOptions={{
              color: "#ef4444",
              weight: 2,
              opacity: 0.8,
              fillColor: "#ef4444",
              fillOpacity: 0.18,
            }}
          >
            <Popup>
              <strong>Thermal Stress Core</strong>
              <br />
              Coral bleaching scenario
              <br />
              High ecosystem stress
            </Popup>
          </Circle>
        )}

        {scenario === "declining_fishery" &&
          layers.includes("Fisheries") && (
            <Polygon
              positions={[
                [latitude + 0.24, longitude - 0.30],
                [latitude + 0.31, longitude + 0.20],
                [latitude - 0.16, longitude + 0.32],
                [latitude - 0.27, longitude - 0.20],
              ]}
              pathOptions={{
                color: "#facc15",
                weight: 2,
                opacity: 0.65,
                fillColor: "#facc15",
                fillOpacity: 0.08,
                dashArray: "6 6",
              }}
            >
              <Popup>
                <strong>Fisheries Pressure Zone</strong>
                <br />
                Elevated vessel activity
                <br />
                Declining fishery scenario
              </Popup>
            </Polygon>
          )}

        {scenario === "healthy_reef" && layers.includes("Ocean") && (
          <Circle
            center={[latitude - 0.01, longitude + 0.01]}
            radius={12 * 1000}
            pathOptions={{
              color: "#38bdf8",
              weight: 2,
              opacity: 0.65,
              fillColor: "#38bdf8",
              fillOpacity: 0.08,
              dashArray: "4 6",
            }}
          >
            <Popup>
              <strong>Healthy Reef Zone</strong>
              <br />
              Stable baseline conditions
            </Popup>
          </Circle>
        )}

        {markers.map((marker) => (
          <CircleMarker
            key={marker.id}
            center={[marker.lat, marker.lon]}
            radius={7}
            pathOptions={{
              color: "#ffffff",
              weight: 2,
              fillColor: MARKER_COLORS[marker.severity],
              fillOpacity: 1,
            }}
          >
            <Popup>
              <strong>{marker.label}</strong>
              <br />
              Type: {marker.kind}
              <br />
              Severity: {marker.severity}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    );
  }

  return {
    default: ClientMap,
  };
});

export function RegionMap({
  result,
  loading,
}: {
  result: AnalysisResult | null;
  loading: boolean;
}) {
  /*
   * IMPORTANT:
   * Every hook is declared before any conditional return.
   * This fixes the "Rendered more hooks than during the previous render"
   * error that was crashing the page.
   */
  const [layers, setLayers] = useState<Layer[]>([...LAYERS]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const latitude =
    typeof result?.region?.latitude === "number"
      ? result.region.latitude
      : typeof result?.region?.center?.lat === "number"
        ? result.region.center.lat
        : null;

  const longitude =
    typeof result?.region?.longitude === "number"
      ? result.region.longitude
      : typeof result?.region?.center?.lon === "number"
        ? result.region.center.lon
        : null;

  const scenario: ScenarioId = result?.scenario ?? "coral_bleaching";
  const config = SCENARIO_CONFIG[scenario];

  const backendMarkers = Array.isArray(result?.markers)
    ? result.markers
    : [];

  /*
   * This hook MUST stay above the conditional returns.
   */
  const markers = useMemo(() => {
    if (!result || latitude === null || longitude === null) {
      return [];
    }

    if (backendMarkers.length > 0) {
      return backendMarkers;
    }

    return scenarioMarkers(
      scenario,
      latitude,
      longitude,
      result.level,
    );
  }, [
    result,
    backendMarkers,
    scenario,
    latitude,
    longitude,
  ]);

  const visibleMarkers = useMemo(
    () =>
      markers.filter((marker) =>
        markerVisible(marker, layers),
      ),
    [markers, layers],
  );

  /*
   * Now conditional rendering is safe because ALL hooks have already
   * executed above.
   */
  if (loading || !result) {
    return (
      <div className="panel p-5">
        <Skeleton className="h-[420px] w-full" />
      </div>
    );
  }

  if (
    latitude === null ||
    longitude === null ||
    !Number.isFinite(latitude) ||
    !Number.isFinite(longitude)
  ) {
    return (
      <section className="panel p-5">
        <div className="flex min-h-[420px] items-center justify-center">
          <div className="text-center">
            <p className="font-display text-lg text-foreground">
              Map unavailable
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              Region coordinates are missing from the analysis response.
            </p>
          </div>
        </div>
      </section>
    );
  }

  const style = LEVEL_STYLES[result.level];

  const impactRadius =
    scenario === "coral_bleaching"
      ? 34
      : scenario === "declining_fishery"
        ? 27
        : 20;

  const impactColor =
    scenario === "coral_bleaching"
      ? "#ef4444"
      : scenario === "declining_fishery"
        ? "#facc15"
        : "#38bdf8";

  return (
    <section className="panel overflow-hidden">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline px-5 py-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-display text-sm font-medium tracking-wide text-foreground">
              {result.region.name}
            </h2>

            <span
              className="rounded-full border px-2 py-0.5 text-[9px] tracking-[0.12em]"
              style={{
                color: config.accent,
                borderColor: `${config.accent}66`,
                backgroundColor: `${config.accent}12`,
              }}
            >
              {config.label}
            </span>
          </div>

          <p className="mt-1 text-xs text-muted-foreground">
            {config.description} · {latitude.toFixed(2)}°N{" "}
            {Math.abs(longitude).toFixed(2)}°
            {longitude >= 0 ? "E" : "W"}
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
                  setLayers((previous) =>
                    previous.includes(layer)
                      ? previous.filter((item) => item !== layer)
                      : [...previous, layer],
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
        {!mounted ? (
          <Skeleton className="h-[420px] w-full" />
        ) : (
          <Suspense fallback={<Skeleton className="h-[420px] w-full" />}>
            <LeafletMap
              latitude={latitude}
              longitude={longitude}
              zoom={config.zoom}
              scenario={scenario}
              result={result}
              layers={layers}
              markers={visibleMarkers}
              config={config}
              impactRadius={impactRadius}
              impactColor={impactColor}
            />
          </Suspense>
        )}

        <div
          className={cn(
            "absolute right-4 top-4 z-[1000] rounded-full border px-3 py-1 text-[11px] tracking-[0.12em]",
            style.border,
            style.bg,
            style.text,
          )}
        >
          {result.level} · {result.index}
        </div>

        <div className="absolute bottom-4 left-4 z-[1000] flex flex-wrap items-center gap-4 rounded-[10px] border border-hairline bg-surface/90 px-3 py-2 text-[11px] text-muted-foreground backdrop-blur">
          <span className="flex items-center gap-1.5">
            <Thermometer className="size-3.5 text-critical" />
            Stress
          </span>

          <span className="flex items-center gap-1.5">
            <Ship className="size-3.5 text-signal-watch" />
            Vessel
          </span>

          <span className="flex items-center gap-1.5">
            <Dna className="size-3.5 text-signal-stressed" />
            eDNA
          </span>

          <span className="flex items-center gap-1.5">
            <Fish className="size-3.5 text-accent" />
            Fisheries
          </span>
        </div>

        {backendMarkers.length === 0 && (
          <div className="absolute bottom-4 right-4 z-[1000] rounded-full border border-hairline bg-surface/90 px-3 py-1.5 text-[10px] tracking-wide text-muted-foreground backdrop-blur">
            DEMO SIGNALS
          </div>
        )}
      </div>
    </section>
  );
}