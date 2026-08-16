import type { IndexLevel, ScenarioId } from "./types";

/** Single source of truth for the alert gate threshold. */
export const ALERT_THRESHOLD = 70;

/** Analyses older than this are considered stale by the alert gate. */
export const STALE_AFTER_MS = 1000 * 60 * 60 * 24;

/**
 * Backend base URL.
 *
 * Development:
 *   http://127.0.0.1:8000
 *
 * The frontend communicates with the existing OceanPulse FastAPI
 * backend. The backend remains responsible for data fallback,
 * fusion/scoring, and alert-gate decisions.
 */
export const API_BASE_URL =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ||
  "http://127.0.0.1:8000";

export const BACKEND_ENABLED = true;

export const SCENARIOS: {
  id: ScenarioId;
  label: string;
  blurb: string;
}[] = [
  {
    id: "healthy_reef",
    label: "Healthy Reef",
    blurb: "Baseline reef conditions",
  },
  {
    id: "declining_fishery",
    label: "Declining Fishery",
    blurb: "CPUE decline signal",
  },
  {
    id: "coral_bleaching",
    label: "Coral Bleaching",
    blurb: "Thermal stress event",
  },
];

export const PERIODS = ["Last 7 days", "Last 30 days", "Last 90 days"];

export const DEFAULT_PERIOD = "Last 30 days";

export function classifyIndex(index: number): IndexLevel {
  if (index >= 80) return "CRITICAL";
  if (index >= 60) return "STRESSED";
  if (index >= 30) return "WATCH";
  return "STABLE";
}

export const LEVEL_STYLES: Record<
  IndexLevel,
  { text: string; bg: string; border: string; dot: string }
> = {
  STABLE: {
    text: "text-silver",
    bg: "bg-transparent",
    border: "border-slate",
    dot: "bg-silver",
  },
  WATCH: {
    text: "text-signal-watch",
    bg: "bg-signal-watch/10",
    border: "border-signal-watch/35",
    dot: "bg-signal-watch",
  },
  STRESSED: {
    text: "text-signal-stressed",
    bg: "bg-signal-stressed/10",
    border: "border-signal-stressed/35",
    dot: "bg-signal-stressed",
  },
  CRITICAL: {
    text: "text-critical",
    bg: "bg-critical/10",
    border: "border-critical/40",
    dot: "bg-critical",
  },
};