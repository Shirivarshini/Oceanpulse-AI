import { Activity, Waves } from "lucide-react";
import type { SourceStatus } from "@/lib/oceanpulse/types";
import { DataSourceLabel } from "./DataSourceLabel";

const LINKS = ["Data", "Regions", "Species", "About"];

export function Navbar({
  onRunAnalysis,
  status,
}: {
  onRunAnalysis: () => void;
  status?: SourceStatus | undefined;
}) {
  return (
    <header className="sticky top-0 z-30 border-b border-hairline bg-background/90 backdrop-blur">
      <div className="mx-auto grid h-16 w-full max-w-[1520px] grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-5 sm:px-6">
        <a href="/" className="flex min-w-0 items-center gap-2.5">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-[10px] border border-hairline-strong bg-elevated">
            <Waves className="size-4 text-accent" />
          </span>
          <span className="font-display truncate text-2xl leading-none text-foreground">
            OceanPulse<span className="text-accent"> AI</span>
          </span>
          {status && <DataSourceLabel status={status} className="ml-2 hidden sm:inline-flex" />}
        </a>

        <div className="flex items-center gap-5">
          <nav className="hidden items-center gap-6 lg:flex">
            {LINKS.map((link) => (
              <a
                key={link}
                href="#"
                className="text-sm text-muted-foreground transition-colors hover:text-body"
              >
                {link}
              </a>
            ))}
          </nav>
          <button className="hidden rounded-full border border-steel px-4 py-1.5 text-sm text-body transition-colors hover:bg-elevated sm:inline-flex">
            Sign In
          </button>
          <button
            onClick={onRunAnalysis}
            className="inline-flex shrink-0 items-center gap-2 rounded-full bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Activity className="size-3.5" />
            <span className="hidden sm:inline">Run Analysis</span>
            <span className="sm:hidden">Run</span>
          </button>
        </div>
      </div>
    </header>
  );
}
