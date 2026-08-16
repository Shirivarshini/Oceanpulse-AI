import type { Analysis, Scenario, SpeciesMatch } from "./types";

// Placeholder fixtures for Task 2 (shell only). Task 3 replaces these with
// POST /api/demo/analyze responses — the UI renders whatever it is given.

const base = (over: Partial<Analysis>): Analysis => ({
  analysis_id: "analysis-001",
  region: {
    id: "gulf-of-mannar",
    name: "Gulf of Mannar",
    latitude: 9.0,
    longitude: 79.0,
  },
  index: 22,
  level: "STABLE",
  confidence: 0.9,
  factors: [],
  timeline: [],
  alert: { status: "NO_ALERT", threshold: 70, reason: "Index below threshold." },
  sources: { ocean: "DEMO", fisheries: "DEMO", molecular: "DEMO" },
  created_at: "2026-08-15T12:00:00Z",
  ...over,
});

export const DEMO_ANALYSES: Record<Scenario, Analysis> = {
  healthy_reef: base({
    analysis_id: "analysis-healthy",
    index: 22,
    level: "STABLE",
    confidence: 0.88,
    factors: [
      {
        name: "Sea Surface Temperature Anomaly",
        category: "ocean",
        impact: 8,
        severity: "low",
        description: "Temperature within seasonal baseline.",
      },
      {
        name: "CPUE Stability",
        category: "fisheries",
        impact: 7,
        severity: "low",
        description: "Catch-per-unit-effort steady across landings.",
      },
      {
        name: "Species Richness",
        category: "molecular",
        impact: 7,
        severity: "low",
        description: "eDNA richness consistent with reference surveys.",
      },
    ],
    timeline: [
      { timestamp: "2026-08-12T10:00:00Z", index: 20, event: "Baseline" },
      { timestamp: "2026-08-13T10:00:00Z", index: 21, event: "No change" },
      { timestamp: "2026-08-14T10:00:00Z", index: 22, event: "Stable conditions" },
    ],
  }),
  declining_fishery: base({
    analysis_id: "analysis-fishery",
    index: 55,
    level: "WATCH",
    confidence: 0.84,
    factors: [
      {
        name: "CPUE Decline",
        category: "fisheries",
        impact: 24,
        severity: "medium",
        description: "Catch-per-unit-effort shows a declining trend.",
      },
      {
        name: "Sea Surface Temperature Anomaly",
        category: "ocean",
        impact: 18,
        severity: "medium",
        description: "Mild warm anomaly persisting over the region.",
      },
      {
        name: "Reduced Species Richness",
        category: "molecular",
        impact: 13,
        severity: "low",
        description: "Slight reduction in observed richness.",
      },
    ],
    timeline: [
      { timestamp: "2026-08-12T10:00:00Z", index: 28, event: "Baseline" },
      { timestamp: "2026-08-13T10:00:00Z", index: 44, event: "Landings drop reported" },
      { timestamp: "2026-08-14T10:00:00Z", index: 55, event: "Watch level reached" },
    ],
    sources: { ocean: "DEMO", fisheries: "HISTORICAL", molecular: "DEMO" },
  }),
  coral_bleaching: base({
    analysis_id: "analysis-001",
    index: 88,
    level: "CRITICAL",
    confidence: 0.91,
    factors: [
      {
        name: "Sea Surface Temperature Anomaly",
        category: "ocean",
        impact: 31,
        severity: "high",
        description: "Elevated temperature signal detected.",
      },
      {
        name: "CPUE Decline",
        category: "fisheries",
        impact: 22,
        severity: "medium",
        description: "Catch-per-unit-effort shows a declining trend.",
      },
      {
        name: "Reduced Species Richness",
        category: "molecular",
        impact: 19,
        severity: "high",
        description: "eDNA results indicate reduced observed richness.",
      },
    ],
    timeline: [
      { timestamp: "2026-08-12T10:00:00Z", index: 28, event: "Baseline" },
      { timestamp: "2026-08-13T10:00:00Z", index: 55, event: "Environmental stress increased" },
      { timestamp: "2026-08-14T10:00:00Z", index: 88, event: "Critical threshold crossed" },
    ],
    alert: {
      status: "ALERT_DISPATCHED",
      threshold: 70,
      reason: "Ecosystem index exceeded configured alert threshold.",
    },
  }),
};

export const SCENARIOS: { id: Scenario; label: string }[] = [
  { id: "healthy_reef", label: "Healthy Reef" },
  { id: "declining_fishery", label: "Declining Fishery" },
  { id: "coral_bleaching", label: "Coral Bleaching" },
];

export const DEMO_SPECIES: SpeciesMatch[] = [
  { taxon: "Acropora cytherea", match_confidence: 0.96, status: "common", source: "DEMO" },
  { taxon: "Chelonia mydas", match_confidence: 0.91, status: "rare", source: "DEMO" },
  { taxon: "Halophila ovalis", match_confidence: 0.87, status: "common", source: "DEMO" },
  { taxon: "Pterois miles", match_confidence: 0.79, status: "invasive", source: "DEMO" },
];
