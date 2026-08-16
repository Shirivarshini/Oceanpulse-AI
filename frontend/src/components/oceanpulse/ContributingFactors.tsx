import { Waves, Fish, Dna } from "lucide-react";
import type { Factor } from "@/lib/oceanpulse/types";

const ICON = { ocean: Waves, fisheries: Fish, molecular: Dna } as const;

export function ContributingFactors({ factors }: { factors: Factor[] }) {
  return (
    <section className="rounded-[10px] bg-trench p-6">
      <h3 className="text-[15px] font-medium tracking-wide text-sea-fog uppercase">
        Contributing factors
      </h3>

      <ul className="mt-4">
        {factors.map((factor) => {
          const Icon = ICON[factor.category];
          const major = factor.severity === "high";
          return (
            <li
              key={factor.name}
              className="flex items-start gap-3 border-b border-reef-shadow py-3 last:border-b-0"
            >
              <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full border border-reef-shadow">
                <Icon className="size-4 text-slate-tide" strokeWidth={1} />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-[15px] text-shell">{factor.name}</p>
                  <span className="flex items-center gap-2">
                    <span className="text-[13px] text-sea-fog">+{factor.impact}</span>
                    <span
                      aria-label={`${factor.severity} severity`}
                      className={`size-2 rounded-full ${major ? "bg-coral-alert" : "bg-bioluminescence"}`}
                    />
                  </span>
                </div>
                <p className="mt-1 text-[13px] text-slate-tide">{factor.description}</p>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
