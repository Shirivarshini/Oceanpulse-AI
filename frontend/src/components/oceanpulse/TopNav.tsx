import { Link } from "@tanstack/react-router";
import { Activity } from "lucide-react";

const MENU = ["Data", "Regions", "Species", "About"];

export function TopNav({ onRunAnalysis }: { onRunAnalysis?: () => void }) {
  return (
    <header className="sticky top-0 z-20 border-b border-reef-shadow bg-abyss/90 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-[1216px] items-center justify-between gap-6 px-6">
        <Link to="/" className="flex items-center gap-2">
          <Activity className="size-5 text-bioluminescence" strokeWidth={1.5} />
          <span className="font-display text-[18px] text-surf-white">OceanPulse</span>
        </Link>

        <ul className="hidden items-center gap-7 md:flex">
          {MENU.map((item) => (
            <li key={item}>
              <span className="cursor-default text-[15px] text-sea-fog transition-colors hover:text-shell">
                {item}
              </span>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className="hidden rounded-full px-4 py-2 text-[15px] text-sea-fog transition-colors hover:text-shell sm:block"
          >
            Sign in
          </button>
          <button
            type="button"
            onClick={onRunAnalysis}
            className="rounded-full bg-surf-white px-4 py-2 text-[15px] font-medium text-abyss transition-opacity hover:opacity-90"
          >
            Run Analysis
          </button>
        </div>
      </nav>
    </header>
  );
}
