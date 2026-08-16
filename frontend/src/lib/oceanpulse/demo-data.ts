import { ALERT_THRESHOLD, classifyIndex } from "./config";
import type {
  AnalysisResult,
  ContributingFactor,
  DataSource,
  MapMarker,
  Region,
  ScenarioId,
  SpeciesMatch,
  TimelinePoint,
} from "./types";

export const GULF_OF_MANNAR: Region = {
  id: "gulf_of_mannar",
  name: "Gulf of Mannar",
  country: "India",
  center: { lat: 9.1, lon: 79.1 },
  bbox: [78.1, 8.5, 79.9, 9.7],
};

export const REGIONS: Region[] = [
  GULF_OF_MANNAR,
  {
    id: "lakshadweep_sea",
    name: "Lakshadweep Sea",
    country: "India",
    center: { lat: 10.5, lon: 73.6 },
    bbox: [72.4, 9.6, 74.6, 11.6],
  },
  {
    id: "andaman_shelf",
    name: "Andaman Shelf",
    country: "India",
    center: { lat: 11.7, lon: 92.7 },
    bbox: [91.8, 10.6, 93.6, 12.8],
  },
];

const DEMO_SOURCES: DataSource[] = [
  { id: "sst", name: "Sea Surface Temperature", status: "DEMO", detail: "Gridded SST anomaly composite" },
  { id: "cpue", name: "Fisheries CPUE", status: "DEMO", detail: "Landing-site catch-per-unit-effort" },
  { id: "ais", name: "Vessel Activity", status: "DEMO", detail: "Aggregated vessel track density" },
  { id: "edna", name: "eDNA Sequencing", status: "DEMO", detail: "Barcode reads, confidence-scored" },
];

interface ScenarioSpec {
  index: number;
  confidence: number;
  factors: ContributingFactor[];
  trend: { day: number; index: number; event: string | null }[];
  species: SpeciesMatch[];
  markers: MapMarker[];
}

const SCENARIO_SPECS: Record<ScenarioId, ScenarioSpec> = {
  healthy_reef: {
    index: 22,
    confidence: 0.88,
    factors: [
      { key: "ocean_temperature", name: "Ocean Temperature", impact: 8, severity: "low", explanation: "SST within seasonal envelope" },
      { key: "fisheries_pressure", name: "Fisheries Pressure", impact: 6, severity: "low", explanation: "CPUE stable across landing sites" },
      { key: "biodiversity", name: "Biodiversity", impact: 5, severity: "low", explanation: "Species richness near baseline" },
      { key: "vessel_activity", name: "Vessel Activity", impact: 3, severity: "low", explanation: "Vessel density below average" },
    ],
    trend: [
      { day: 1, index: 20, event: "Baseline established" },
      { day: 7, index: 21, event: null },
      { day: 14, index: 23, event: "Minor turbidity pulse" },
      { day: 21, index: 22, event: null },
      { day: 30, index: 22, event: "Conditions stable" },
    ],
    species: [
      { sample_id: "GM-S-014", taxon: "Acropora sp.", confidence: 0.96, status: "common", sample_date: "2026-08-02", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-015", taxon: "Chaetodon collare", confidence: 0.9, status: "common", sample_date: "2026-08-05", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-016", taxon: "Halophila ovalis", confidence: 0.84, status: "common", sample_date: "2026-08-09", reference: "Barcode ref DB v4", source: "DEMO" },
    ],
    markers: [
      { id: "m1", kind: "station", label: "Reef station A", lat: 9.22, lon: 79.05, severity: "low" },
      { id: "m2", kind: "edna", label: "eDNA sample GM-S-014", lat: 9.02, lon: 79.32, severity: "low" },
      { id: "m3", kind: "vessel", label: "Trawler cluster", lat: 8.86, lon: 78.72, severity: "low" },
    ],
  },
  declining_fishery: {
    index: 55,
    confidence: 0.86,
    factors: [
      { key: "fisheries_pressure", name: "Fisheries Pressure", impact: 24, severity: "high", explanation: "Sustained CPUE decline detected" },
      { key: "vessel_activity", name: "Vessel Activity", impact: 15, severity: "moderate", explanation: "Effort concentrated on shrinking grounds" },
      { key: "biodiversity", name: "Biodiversity", impact: 10, severity: "moderate", explanation: "Fewer target-taxon detections" },
      { key: "ocean_temperature", name: "Ocean Temperature", impact: 6, severity: "low", explanation: "SST anomaly mild and intermittent" },
    ],
    trend: [
      { day: 1, index: 34, event: "Effort increase logged" },
      { day: 7, index: 41, event: "CPUE decline detected" },
      { day: 14, index: 47, event: null },
      { day: 21, index: 52, event: "Target taxa detections fall" },
      { day: 30, index: 55, event: "Watch condition sustained" },
    ],
    species: [
      { sample_id: "GM-S-081", taxon: "Unknown Serranidae", confidence: 0.79, status: "rare", sample_date: "2026-08-04", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-082", taxon: "Rastrelliger kanagurta", confidence: 0.88, status: "common", sample_date: "2026-08-08", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-083", taxon: "Introduced taxon", confidence: 0.71, status: "invasive", sample_date: "2026-08-12", reference: "Barcode ref DB v4", source: "DEMO" },
    ],
    markers: [
      { id: "m1", kind: "vessel", label: "Trawler cluster", lat: 8.9, lon: 78.66, severity: "high" },
      { id: "m2", kind: "vessel", label: "Effort hotspot", lat: 9.05, lon: 78.9, severity: "moderate" },
      { id: "m3", kind: "edna", label: "eDNA sample GM-S-081", lat: 9.18, lon: 79.28, severity: "moderate" },
      { id: "m4", kind: "station", label: "Reef station C", lat: 9.32, lon: 79.5, severity: "low" },
    ],
  },
  coral_bleaching: {
    index: 88,
    confidence: 0.91,
    factors: [
      { key: "ocean_temperature", name: "Ocean Temperature", impact: 31, severity: "severe", explanation: "Elevated SST anomaly" },
      { key: "fisheries_pressure", name: "Fisheries Pressure", impact: 22, severity: "high", explanation: "CPUE decline detected" },
      { key: "biodiversity", name: "Biodiversity", impact: 19, severity: "high", explanation: "Reduced species richness" },
      { key: "vessel_activity", name: "Vessel Activity", impact: 16, severity: "moderate", explanation: "Increased fishing pressure" },
    ],
    trend: [
      { day: 1, index: 28, event: "Baseline index 28" },
      { day: 7, index: 40, event: "Temperature anomaly detected" },
      { day: 14, index: 55, event: "CPUE decline detected" },
      { day: 21, index: 72, event: "Alert threshold crossed" },
      { day: 30, index: 88, event: "eDNA species richness decreases" },
    ],
    species: [
      { sample_id: "GM-S-201", taxon: "Acropora sp.", confidence: 0.94, status: "common", sample_date: "2026-08-03", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-202", taxon: "Unknown Serranidae", confidence: 0.81, status: "rare", sample_date: "2026-08-07", reference: "Barcode ref DB v4", source: "DEMO" },
      { sample_id: "GM-S-203", taxon: "Introduced taxon", confidence: 0.76, status: "invasive", sample_date: "2026-08-11", reference: "Barcode ref DB v4", source: "DEMO" },
    ],
    markers: [
      { id: "m1", kind: "station", label: "Bleaching front", lat: 9.12, lon: 79.12, severity: "severe" },
      { id: "m2", kind: "station", label: "Thermal station B", lat: 8.95, lon: 79.45, severity: "high" },
      { id: "m3", kind: "edna", label: "eDNA sample GM-S-201", lat: 9.3, lon: 79.3, severity: "high" },
      { id: "m4", kind: "vessel", label: "Trawler cluster", lat: 8.82, lon: 78.7, severity: "moderate" },
      { id: "m5", kind: "vessel", label: "Effort hotspot", lat: 9.0, lon: 78.85, severity: "moderate" },
    ],
  },
};

const DAY_LABELS: Record<number, string> = { 1: "Day 1", 7: "Day 7", 14: "Day 14", 21: "Day 21", 30: "Day 30" };

function buildTimeline(spec: ScenarioSpec): TimelinePoint[] {
  return spec.trend.map((p) => ({
    day: p.day,
    label: DAY_LABELS[p.day] ?? `Day ${p.day}`,
    index: p.index,
    level: classifyIndex(p.index),
    event: p.event,
  }));
}

export function buildDemoAnalysis(
  scenario: ScenarioId,
  region: Region = GULF_OF_MANNAR,
  period = "Last 30 days",
): AnalysisResult {
  const spec = SCENARIO_SPECS[scenario];
  const index = spec.index;
  const dispatched = index >= ALERT_THRESHOLD;
  const createdAt = "2026-08-15T00:00:00.000Z";

  return {
    analysis_id: `demo_${scenario}_${region.id}`,
    region,
    scenario,
    period,
    index,
    level: classifyIndex(index),
    confidence: spec.confidence,
    factors: spec.factors,
    timeline: buildTimeline(spec),
    alert: {
      threshold: ALERT_THRESHOLD,
      index,
      decision: dispatched ? "ALERT_DISPATCHED" : "NO_ALERT",
      reason: dispatched
        ? "Index exceeded the configured ecosystem-risk threshold."
        : "Index remained below the configured ecosystem-risk threshold.",
      evaluated_at: createdAt,
    },
    species: spec.species,
    markers: spec.markers,
    sources: DEMO_SOURCES,
    source: "DEMO",
    created_at: createdAt,
  };
}
