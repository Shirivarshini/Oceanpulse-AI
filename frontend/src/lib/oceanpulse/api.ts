import { API_BASE_URL } from "./config";
import { REGIONS, GULF_OF_MANNAR } from "./demo-data";
import type {
  AnalysisResult,
  AnalyzeRequest,
  DemoAnalyzeRequest,
  HealthResponse,
  Region,
  ScenarioId,
  SpeciesMatch,
  TimelinePoint,
  DataSource,
  MapMarker,
  ContributingFactor,
} from "./types";

const TIMEOUT_MS = 5000;

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const controller = new AbortController();

  const timer = setTimeout(() => {
    controller.abort();
  }, TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "content-type": "application/json",
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      const message = await response.text().catch(() => "");
      throw new Error(
        message || `Request failed with status ${response.status}`,
      );
    }

    return (await response.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * GET /health
 */
export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/**
 * POST /api/demo/analyze
 *
 * This is the primary endpoint currently used by the dashboard.
 *
 * The Backend owns:
 * - data fallback
 * - source selection
 * - fusion/scoring
 * - confidence
 * - alert gate
 *
 * The frontend only adapts the response for presentation.
 */
export async function demoAnalyze(
  body: DemoAnalyzeRequest,
): Promise<AnalysisResult> {
  const response = await request<BackendAnalysisResponse>(
    "/api/demo/analyze",
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );

  return adaptBackendAnalysis(response, body.scenario);
}

/**
 * POST /api/analyze
 *
 * Kept available for future non-demo integration.
 */
export async function analyze(
  body: AnalyzeRequest,
): Promise<AnalysisResult> {
  const response = await request<BackendAnalysisResponse>(
    "/api/analyze",
    {
      method: "POST",
      body: JSON.stringify({
        region_id: body.region_id,
        scenario: body.scenario,
        period: body.period,
      }),
    },
  );

  return adaptBackendAnalysis(response, body.scenario, body.period);
}

/**
 * GET /api/region/{id}
 */
export async function getRegion(id: string): Promise<Region> {
  const response = await request<BackendRegionResponse>(
    `/api/region/${encodeURIComponent(id)}`,
  );

  return {
    id: response.id,
    name: response.name,
    latitude: response.latitude,
    longitude: response.longitude,
  };
}

/**
 * GET /api/insight/{id}
 */
export async function getInsight(
  analysisId: string,
): Promise<AnalysisResult> {
  const response = await request<BackendAnalysisResponse>(
    `/api/insight/${encodeURIComponent(analysisId)}`,
  );

  return adaptBackendAnalysis(response, "coral_bleaching");
}

/**
 * GET /api/timeline/{id}
 */
export async function getTimeline(
  analysisId: string,
): Promise<TimelinePoint[]> {
  const response = await request<BackendTimelineResponse>(
    `/api/timeline/${encodeURIComponent(analysisId)}`,
  );

  return response.timeline.map((point) => ({
    timestamp: point.timestamp,
    index: point.index,
    event: point.event,
  }));
}

/**
 * GET /api/species/{id}
 */
export async function getSpecies(
  regionId: string,
): Promise<SpeciesMatch[]> {
  const response = await request<BackendSpeciesResponse>(
    `/api/species/${encodeURIComponent(regionId)}`,
  );

  return response.species;
}

/**
 * GET /api/edna/matches/{sample_id}
 *
 * This route exists in the frontend contract but is not currently
 * registered by the Backend shown in this project.
 *
 * Keep this function available for future Backend eDNA integration.
 */
export async function getEdnaMatches(
  sampleId: string,
): Promise<SpeciesMatch[]> {
  throw new Error(
    `eDNA match endpoint is not currently exposed by the Backend: ${sampleId}`,
  );
}

/* -------------------------------------------------------------------------- */
/* Backend response types                                                     */
/* -------------------------------------------------------------------------- */

interface BackendAnalysisResponse {
  analysis_id: string;
  region: {
    id: string;
    name: string;
    latitude: number;
    longitude: number;
  };
  index: number;
  level: AnalysisResult["level"];
  confidence: number;
  factors: Array<{
    name: string;
    category: "ocean" | "fisheries" | "molecular";
    impact: number;
    severity: "low" | "medium" | "high";
    description: string;
  }>;
  timeline: Array<{
    timestamp: string;
    index: number;
    event: string;
  }>;
  alert: {
    status: AnalysisResult["alert"]["status"];
    threshold: number;
    reason: string;
  };
  sources: {
    ocean: SourceStatus;
    fisheries: SourceStatus;
    molecular: SourceStatus;
  };
  created_at: string;
}

interface BackendRegionResponse {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  bounding_box?: {
    min_lat: number;
    max_lat: number;
    min_lon: number;
    max_lon: number;
  };
  source?: SourceStatus;
}

interface BackendTimelineResponse {
  analysis_id: string;
  timeline: Array<{
    timestamp: string;
    index: number;
    event: string;
  }>;
  source: SourceStatus;
}

interface BackendSpeciesResponse {
  region_id: string;
  species: SpeciesMatch[];
}

/* -------------------------------------------------------------------------- */
/* Response adapter                                                            */
/* -------------------------------------------------------------------------- */

function adaptBackendAnalysis(
  response: BackendAnalysisResponse,
  scenario: ScenarioId,
  period = "Last 30 days",
): AnalysisResult {
  const primarySource = selectPrimarySource(response.sources);

  const region = {
    id: response.region.id,
    name: response.region.name,
    latitude: response.region.latitude,
    longitude: response.region.longitude,
  };

  const factors: ContributingFactor[] = response.factors.map((factor) => ({
    name: factor.name,
    category: factor.category,
    impact: factor.impact,
    severity: factor.severity,
    description: factor.description,
  }));

  const timeline: TimelinePoint[] = response.timeline.map((point) => ({
    timestamp: point.timestamp,
    index: point.index,
    event: point.event,
  }));

  const alert = {
    threshold: response.alert.threshold,
    index: response.index,
    status: response.alert.status,
    reason: response.alert.reason,
  };

  return {
    analysis_id: response.analysis_id,
    region,
    scenario,
    period,
    index: response.index,
    level: response.level,
    confidence: response.confidence,
    factors,
    timeline,
    alert,
    species: [],
    markers: buildDemoMarkers(region.latitude, region.longitude),
    sources: buildDataSources(response.sources),
    source: primarySource,
    created_at: response.created_at,
  };
}

/**
 * The Backend gives source provenance per category.
 *
 * There is no single Backend "primary source" field, so the frontend
 * uses the highest-priority source actually selected across categories
 * purely for display.
 *
 * This does NOT alter or infer Backend provenance.
 */
function selectPrimarySource(
  sources: BackendAnalysisResponse["sources"],
): SourceStatus {
  const priority: SourceStatus[] = [
    "LIVE",
    "CACHED",
    "HISTORICAL",
    "DEMO",
  ];

  for (const status of priority) {
    if (
      sources.ocean === status ||
      sources.fisheries === status ||
      sources.molecular === status
    ) {
      return status;
    }
  }

  return "DEMO";
}

function buildDataSources(
  sources: BackendAnalysisResponse["sources"],
): DataSource[] {
  return [
    {
      id: "ocean",
      name: "Oceanographic",
      status: sources.ocean,
      detail: `Backend-selected source: ${sources.ocean}`,
    },
    {
      id: "fisheries",
      name: "Fisheries",
      status: sources.fisheries,
      detail: `Backend-selected source: ${sources.fisheries}`,
    },
    {
      id: "molecular",
      name: "Molecular / eDNA",
      status: sources.molecular,
      detail: `Backend-selected source: ${sources.molecular}`,
    },
  ];
}

function buildDemoMarkers(
  latitude: number,
  longitude: number,
): MapMarker[] {
  return [
    {
      id: "region-station",
      kind: "station",
      label: "Monitoring region",
      lat: latitude,
      lon: longitude,
      severity: "low",
    },
  ];
}