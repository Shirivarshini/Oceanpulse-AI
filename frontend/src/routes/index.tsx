import { createFileRoute } from "@tanstack/react-router";
import { AlertGate } from "@/components/oceanpulse/AlertGate";
import { ContributingFactors } from "@/components/oceanpulse/ContributingFactors";
import { ControlBar } from "@/components/oceanpulse/ControlBar";
import { DataSources } from "@/components/oceanpulse/DataSources";
import { EcosystemIndexCard } from "@/components/oceanpulse/EcosystemIndexCard";
import { ErrorState } from "@/components/oceanpulse/ErrorState";
import { Footer } from "@/components/oceanpulse/Footer";
import { IndexTrendChart } from "@/components/oceanpulse/IndexTrendChart";
import { ModelInsights } from "@/components/oceanpulse/ModelInsights";
import { MolecularBiodiversity } from "@/components/oceanpulse/MolecularBiodiversity";
import { Navbar } from "@/components/oceanpulse/Navbar";
import { Panel } from "@/components/oceanpulse/Panel";
import { RegionMap } from "@/components/oceanpulse/RegionMap";
import { Timeline } from "@/components/oceanpulse/Timeline";
import { DataSourceLabel } from "@/components/oceanpulse/DataSourceLabel";
import { useAnalysis } from "@/lib/oceanpulse/use-analysis";

const TITLE = "OceanPulse AI — Marine Ecosystem Intelligence Console";
const DESCRIPTION =
  "Fuse oceanographic, fisheries and eDNA signals into an explainable 0–100 ecosystem index with alert gating for marine regions.";

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
  const {
    regions,
    regionId,
    scenario,
    period,
    result,
    loading,
    error,
    run,
    selectRegion,
    selectScenario,
    selectPeriod,
  } = useAnalysis();

  const status = result?.source ?? "DEMO";
  const dataState = loading ? "LOADING" : error ? "UNAVAILABLE" : result ? "LOADED" : "IDLE";

  return (
    <div className="min-h-screen bg-background">
      <Navbar onRunAnalysis={run} status={result ? status : undefined} />

      <main className="mx-auto w-full max-w-[1520px] space-y-4 px-5 py-7 sm:px-6 sm:py-9">
        {/* Hero band */}
        <section className="tile grid gap-6 p-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)] lg:items-end lg:p-8">
          <div
            className="hatch pointer-events-none absolute inset-y-0 right-0 hidden w-52 opacity-30 lg:block"
            aria-hidden
          />
          <div className="relative min-w-0">
            <p className="label-caps text-accent">Insight Fusion Engine</p>
            <h1 className="font-display mt-3 text-[clamp(2.25rem,5.4vw,3.75rem)] leading-[1.04] text-foreground">
              Marine ecosystem condition console
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-muted-foreground">
              Ocean, fisheries and eDNA signals fused into one ecosystem index — explained factor by
              factor, then gated for alerting. Decision support, not a definitive scientific
              conclusion.
            </p>
          </div>

          <dl className="relative grid grid-cols-2 gap-x-5 gap-y-4 border-t border-hairline pt-5 lg:border-t-0 lg:border-l lg:pt-0 lg:pl-8">
            <div className="min-w-0">
              <dt className="label-caps">Region</dt>
              <dd className="mt-1 truncate text-sm text-body">
                {result?.region.name ?? "\u2014"}
              </dd>
            </div>
            <div className="min-w-0">
              <dt className="label-caps">Data state</dt>
              <dd className="mt-1 truncate text-sm text-body">{dataState}</dd>
            </div>
            <div className="min-w-0">
              <dt className="label-caps">Provenance</dt>
              <dd className="mt-1.5">
                <DataSourceLabel status={status} />
              </dd>
            </div>
            <div className="min-w-0">
              <dt className="label-caps">Analysis ID</dt>
              <dd className="mt-1 truncate font-mono text-xs text-muted-foreground">
                {result?.analysis_id ?? "\u2014"}
              </dd>
            </div>
          </dl>
        </section>

        {error && <ErrorState message={error} onRetry={run} />}

        <ControlBar
          regions={regions}
          regionId={regionId}
          scenario={scenario}
          period={period}
          loading={loading}
          onRegionChange={selectRegion}
          onScenarioChange={selectScenario}
          onPeriodChange={selectPeriod}
          onRun={run}
        />

        {/* Bento grid */}
        <div className="grid gap-4 lg:grid-cols-12">
          <div className="lg:col-span-4 [&>*]:h-full">
            <EcosystemIndexCard result={result} loading={loading} />
          </div>
          <div className="lg:col-span-8 [&>*]:h-full">
            <RegionMap result={result} loading={loading} />
          </div>

          <div className="lg:col-span-12 [&>*]:h-full">
            <AlertGate alert={result?.alert ?? null} loading={loading} />
          </div>

          <div className="lg:col-span-4 [&>*]:h-full">
            <ContributingFactors
              factors={result?.factors ?? []}
              source={status}
              loading={loading}
            />
          </div>
          <div className="lg:col-span-8 [&>*]:h-full">
            <Panel
              title="Index Trend"
              subtitle="Backend-provided index across the selected period with the alert threshold."
              right={<DataSourceLabel status={status} />}
            >
              <IndexTrendChart timeline={result?.timeline ?? []} loading={loading} />
            </Panel>
          </div>

          <div className="lg:col-span-4 [&>*]:h-full">
            <Timeline timeline={result?.timeline ?? []} source={status} loading={loading} />
          </div>
          <div className="lg:col-span-4 [&>*]:h-full">
            <DataSources sources={result?.sources ?? []} loading={loading} />
          </div>
          <div className="lg:col-span-4 [&>*]:h-full">
            <ModelInsights />
          </div>

          <div className="lg:col-span-12 [&>*]:h-full">
            <MolecularBiodiversity
              species={result?.species ?? []}
              source={status}
              loading={loading}
            />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
