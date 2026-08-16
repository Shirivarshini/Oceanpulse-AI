import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";

import { TopNav } from "@/components/oceanpulse/TopNav";
import { ScenarioSelector } from "@/components/oceanpulse/ScenarioSelector";
import { EcosystemIndexCard } from "@/components/oceanpulse/EcosystemIndexCard";
import { ContributingFactors } from "@/components/oceanpulse/ContributingFactors";
import { AlertPanel } from "@/components/oceanpulse/AlertPanel";
import { RegionMapPanel } from "@/components/oceanpulse/RegionMapPanel";
import { SpeciesTable } from "@/components/oceanpulse/SpeciesTable";
import { DEMO_SPECIES } from "@/lib/oceanpulse/demoData";
import { analyzeScenario } from "@/lib/oceanpulse/api";
import type { Analysis, Scenario } from "@/lib/oceanpulse/types";

const TITLE = "OceanPulse — Marine Ecosystem Risk Dashboard";
const DESCRIPTION =
  "Fused ocean, fisheries and eDNA signals into a single ecosystem index with explainable factors, timeline and alert gate status.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const [scenario, setScenario] =
    useState<Scenario>("coral_bleaching");

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAnalysis() {
      setLoading(true);
      setError(null);

      try {
        const result = await analyzeScenario(scenario);

        if (!cancelled) {
          setAnalysis(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load analysis.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAnalysis();

    return () => {
      cancelled = true;
    };
  }, [scenario]);

  if (loading && !analysis) {
    return (
      <div className="min-h-screen bg-abyss">
        <TopNav />

        <main className="mx-auto max-w-[1216px] px-6 pt-10 pb-24">
          <p className="text-[13px] tracking-wide text-slate-tide uppercase">
            Ecosystem monitoring
          </p>

          <p className="mt-4 text-slate-tide">
            Loading analysis...
          </p>
        </main>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="min-h-screen bg-abyss">
        <TopNav />

        <main className="mx-auto max-w-[1216px] px-6 pt-10 pb-24">
          <p className="text-[13px] tracking-wide text-slate-tide uppercase">
            Ecosystem monitoring
          </p>

          <h1 className="mt-2 text-[44px] leading-tight text-surf-white">
            Marine risk, read in one number
          </h1>

          <p className="mt-6 text-coral-alert">
            {error}
          </p>
        </main>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <div className="min-h-screen bg-abyss">
      <TopNav />

      <main className="mx-auto max-w-[1216px] px-6 pt-10 pb-24">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[13px] tracking-wide text-slate-tide uppercase">
              Ecosystem monitoring
            </p>

            <h1 className="mt-2 text-[44px] leading-tight text-surf-white">
              Marine risk, read in one number
            </h1>
          </div>

          <ScenarioSelector
            value={scenario}
            onChange={setScenario}
          />
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="flex flex-col gap-6">
            <EcosystemIndexCard analysis={analysis} />

            <RegionMapPanel analysis={analysis} />
          </div>

          <div className="flex flex-col gap-6">
            <AlertPanel alert={analysis.alert} />

            <ContributingFactors factors={analysis.factors} />

            <SpeciesTable species={DEMO_SPECIES} />
          </div>
        </div>

        <p className="mt-8 text-[13px] text-slate-tide">
          Analysis {analysis.analysis_id} · generated{" "}
          {new Date(analysis.created_at).toUTCString()}
        </p>
      </main>
    </div>
  );
}