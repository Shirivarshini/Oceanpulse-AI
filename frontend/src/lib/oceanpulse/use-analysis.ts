import { useCallback, useEffect, useRef, useState } from "react";
import { demoAnalyze } from "./api";
import { DEFAULT_PERIOD } from "./config";
import { GULF_OF_MANNAR, REGIONS } from "./demo-data";
import type { AnalysisResult, ScenarioId } from "./types";

interface AnalysisState {
  result: AnalysisResult | null;
  loading: boolean;
  error: string | null;
}

/**
 * Shared analysis state for the entire dashboard.
 *
 * The Backend is the source of truth for:
 * - scenario analysis
 * - ecosystem index
 * - confidence
 * - contributing factors
 * - timeline
 * - alert gate
 * - data-source provenance
 *
 * The frontend only requests the analysis and presents the result.
 */
export function useAnalysis() {
  const [regionId, setRegionId] = useState(GULF_OF_MANNAR.id);
  const [scenario, setScenario] =
    useState<ScenarioId>("coral_bleaching");
  const [period, setPeriod] = useState(DEFAULT_PERIOD);

  const [state, setState] = useState<AnalysisState>({
    result: null,
    loading: true,
    error: null,
  });

  const runId = useRef(0);

  const run = useCallback(
    async (overrides?: {
      regionId?: string;
      scenario?: ScenarioId;
      period?: string;
    }) => {
      const selectedScenario =
        overrides?.scenario ?? scenario;

      const selectedRegion =
        overrides?.regionId ?? regionId;

      const selectedPeriod =
        overrides?.period ?? period;

      const id = ++runId.current;

      setState((previous) => ({
        ...previous,
        loading: true,
        error: null,
      }));

      try {
        /*
         * The current Backend integration exposes the deterministic
         * demo-analysis endpoint:
         *
         * POST /api/demo/analyze
         *
         * The Backend itself performs:
         * LIVE → CACHED → HISTORICAL → DEMO
         * source selection,
         * Fusion Engine execution,
         * and Alert Gate evaluation.
         *
         * Do not reproduce those decisions in the frontend.
         */
        const result = await demoAnalyze({
          scenario: selectedScenario,
        });

        if (id !== runId.current) {
          return;
        }

        /*
         * The selected region and period are currently UI controls.
         * The existing demo Backend endpoint accepts only the scenario,
         * so these values are retained locally for the UI without
         * pretending that the Backend used them for scoring.
         */
        const normalizedResult: AnalysisResult = {
          ...result,
          scenario: selectedScenario,
          period: selectedPeriod,
        };

        setState({
          result: normalizedResult,
          loading: false,
          error: null,
        });
      } catch (error) {
        if (id !== runId.current) {
          return;
        }

        const message =
          error instanceof Error
            ? error.message
            : "Analysis unavailable. Please retry.";

        setState({
          result: null,
          loading: false,
          error: message,
        });
      }

      /*
       * selectedRegion is intentionally retained in the request state.
       * The current /api/demo/analyze contract is scenario-based.
       */
      void selectedRegion;
    },
    [regionId, scenario, period],
  );

  useEffect(() => {
    void run();

    // Initial analysis is intentionally triggered once.
    // Subsequent changes use the explicit selectors below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectRegion = useCallback(
    (id: string) => {
      setRegionId(id);
      void run({ regionId: id });
    },
    [run],
  );

  const selectScenario = useCallback(
    (id: ScenarioId) => {
      setScenario(id);
      void run({ scenario: id });
    },
    [run],
  );

  const selectPeriod = useCallback(
    (selectedPeriod: string) => {
      setPeriod(selectedPeriod);
      void run({ period: selectedPeriod });
    },
    [run],
  );

  return {
    regions: REGIONS,
    regionId,
    scenario,
    period,
    ...state,
    run: () => void run(),
    selectRegion,
    selectScenario,
    selectPeriod,
  };
}