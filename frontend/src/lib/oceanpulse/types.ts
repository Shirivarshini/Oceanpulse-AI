// Shapes mirror API_CONTRACT.md exactly. Do not rename fields.

export type IndexLevel = "STABLE" | "WATCH" | "STRESSED" | "CRITICAL";
export type AlertStatus = "NO_ALERT" | "ALERT_DISPATCHED" | "ALERT_BLOCKED_STALE";
export type DataSource = "LIVE" | "CACHED" | "HISTORICAL" | "DEMO";
export type Severity = "low" | "medium" | "high";
export type SpeciesStatus = "common" | "rare" | "invasive";
export type Scenario = "healthy_reef" | "declining_fishery" | "coral_bleaching";

export interface Region {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface Factor {
  name: string;
  category: "ocean" | "fisheries" | "molecular";
  impact: number;
  severity: Severity;
  description: string;
}

export interface TimelinePoint {
  timestamp: string;
  index: number;
  event: string;
}

export interface Alert {
  status: AlertStatus;
  threshold: number;
  reason: string;
}

export interface Analysis {
  analysis_id: string;
  region: Region;
  index: number;
  level: IndexLevel;
  confidence: number;
  factors: Factor[];
  timeline: TimelinePoint[];
  alert: Alert;
  sources: Record<"ocean" | "fisheries" | "molecular", DataSource>;
  created_at: string;
}

export interface SpeciesMatch {
  taxon: string;
  match_confidence: number;
  status: SpeciesStatus;
  source: DataSource;
}

export function levelFromIndex(index: number): IndexLevel {
  if (index >= 80) return "CRITICAL";
  if (index >= 60) return "STRESSED";
  if (index >= 30) return "WATCH";
  return "STABLE";
}

/** Coral Alert is reserved for genuinely critical states. */
export function isCritical(level: IndexLevel) {
  return level === "CRITICAL" || level === "STRESSED";
}
