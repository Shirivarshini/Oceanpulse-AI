export function Footer() {
  return (
    <footer className="mt-10 border-t border-hairline bg-surface">
      <div className="mx-auto flex w-full max-w-[1440px] flex-col gap-3 px-6 py-8 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between">
        <p className="max-w-2xl">
          OceanPulse AI is a decision-support research prototype. Outputs are exploratory signal
          fusion over demo data and are not definitive scientific, regulatory, or legal conclusions.
        </p>
        <p className="shrink-0">Insight Fusion Engine v0.1 &middot; DEMO mode</p>
      </div>
    </footer>
  );
}
