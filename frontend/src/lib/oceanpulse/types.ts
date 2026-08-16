// Types for the existing OceanPulse Backend API.
// These types intentionally mirror the Backend response contract.

export type ScenarioId =
  | "healthy_reef"
  | "declining_fishery"
  | "coral_bleaching";

export type IndexLevel =
  | "STABLE"
  | "WATCH"
  | "STRESSED"
  | "CRITICAL";

export type AlertDecision =
  | "NO_ALERT"
  | "ALERT_DISPATCHED"
  | "ALERT_BLOCKED_STALE";

export type SourceStatus =
  | "LIVE"
  | "CACHED"
  | "HISTORICAL"
  | "DEMO";

export type FactorSeverity =
  | "low"
  | "medium"
  | "high";

export type FactorCategory =
  | "ocean"
  | "fisheries"
  | "molecular";

export interface Region {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface ContributingFactor {
  name: string;
  category: FactorCategory;
  impact: number;
  severity: FactorSeverity;
  description: string;
}

export interface TimelinePoint {
  timestamp: string;
  index: number;
  event: string;
}

export interface AlertGateResult {
  threshold: number;
  index: number;
  status: AlertDecision;
  reason: string;
}

export interface SpeciesMatch {
  taxon: string;
  match_confidence: number;
  status: "common" | "rare" | "invasive";
  source: SourceStatus;
}

export interface BackendSources {
  ocean: SourceStatus;
  fisheries: SourceStatus;
  molecular: SourceStatus;
}

export interface DataSource {
  id: string;
  name: string;
  status: SourceStatus;
  detail: string;
}

export interface MapMarker {
  id: string;
  kind: "vessel" | "edna" | "station";
  label: string;
  lat: number;
  lon: number;
  severity: FactorSeverity;
}

export interface AnalysisResult {
  analysis_id: string;
  region: Region;
  scenario: ScenarioId;
  period: string;
  index: number;
  level: IndexLevel;
  confidence: number;
  factors: ContributingFactor[];
  timeline: TimelinePoint[];
  alert: AlertGateResult;
  species: SpeciesMatch[];
  markers: MapMarker[];
  sources: DataSource[];
  source: SourceStatus;
  created_at: string;
}

export interface AnalyzeRequest {
  region_id: string;
  scenario: ScenarioId;
  period: string;
}

export interface DemoAnalyzeRequest {
  scenario: ScenarioId;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  service: string;
  version: string;
}

export function levelFromIndex(index: number): IndexLevel {
  if (index >= 80) return "CRITICAL";
  if (index >= 60) return "STRESSED";
  if (index >= 30) return "WATCH";
  return "STABLE";
}

export function isCritical(level: IndexLevel): boolean {
  return level === "CRITICAL" || level === "STRESSED";
}