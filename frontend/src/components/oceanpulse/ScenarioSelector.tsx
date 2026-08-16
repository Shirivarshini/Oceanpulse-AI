import { cn } from "@/lib/utils";
import { SCENARIOS } from "@/lib/oceanpulse/config";
import type { ScenarioId } from "@/lib/oceanpulse/types";

export function ScenarioSelector({
  value,
  onChange,
}: {
  value: ScenarioId;
  onChange: (id: ScenarioId) => void;
}) {
  return (
    <div>
      <span className="label-caps">Scenario</span>
      <div className="mt-2 grid gap-2 sm:grid-cols-3">
        {SCENARIOS.map((s) => {
          const active = s.id === value;
          return (
            <button
              key={s.id}
              onClick={() => onChange(s.id)}
              aria-pressed={active}
              className={cn(
                "group rounded-[10px] border px-3.5 py-2.5 text-left transition-colors",
                active
                  ? "border-accent/60 bg-accent/10"
                  : "border-hairline bg-elevated hover:border-hairline-strong",
              )}
            >
              <span
                className={cn(
                  "block truncate text-sm leading-tight",
                  active ? "text-foreground" : "text-body",
                )}
              >
                {s.label}
              </span>
              <span className="mt-0.5 block truncate text-[10px] tracking-wide text-muted-foreground">
                {s.blurb}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
