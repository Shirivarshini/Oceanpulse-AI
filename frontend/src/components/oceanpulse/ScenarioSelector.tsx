import type { Scenario } from "@/lib/oceanpulse/types";
import { SCENARIOS } from "@/lib/oceanpulse/demoData";
import { cn } from "@/lib/utils";

export function ScenarioSelector({
  value,
  onChange,
}: {
  value: Scenario;
  onChange: (scenario: Scenario) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="mr-1 text-[13px] tracking-wide text-slate-tide uppercase">Scenario</span>
      {SCENARIOS.map((scenario) => {
        const active = scenario.id === value;
        return (
          <button
            key={scenario.id}
            type="button"
            onClick={() => onChange(scenario.id)}
            aria-pressed={active}
            className={cn(
              "rounded-full border px-4 py-1.5 text-[15px] transition-colors",
              active
                ? "border-bioluminescence text-bioluminescence"
                : "border-tide-current text-sea-fog hover:text-shell",
            )}
          >
            {scenario.label}
          </button>
        );
      })}
    </div>
  );
}
