import type { SpeciesMatch, SpeciesStatus } from "@/lib/oceanpulse/types";
import { SourceLabel } from "./SourceLabel";

const STATUS_TONE: Record<SpeciesStatus, string> = {
  common: "border-bioluminescence text-bioluminescence",
  rare: "border-coral-alert text-coral-alert",
  invasive: "border-coral-alert text-coral-alert",
};

export function SpeciesTable({ species }: { species: SpeciesMatch[] }) {
  return (
    <section className="rounded-[10px] bg-trench p-6">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-[15px] font-medium tracking-wide text-sea-fog uppercase">
          eDNA species matches
        </h3>
        <SourceLabel source="DEMO" />
      </div>

      <table className="mt-4 w-full border-collapse">
        <thead>
          <tr className="border-b border-reef-shadow text-left">
            <th className="py-2 text-[14px] font-medium text-sea-fog">Taxon</th>
            <th className="py-2 text-[14px] font-medium text-sea-fog">Status</th>
            <th className="py-2 text-right text-[14px] font-medium text-sea-fog">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {species.map((match) => (
            <tr key={match.taxon} className="border-b border-reef-shadow last:border-b-0">
              <td className="py-2.5 text-[15px] text-shell italic">{match.taxon}</td>
              <td className="py-2.5">
                <span
                  className={`inline-flex rounded-full border px-2.5 py-0.5 text-[12px] font-medium ${STATUS_TONE[match.status]}`}
                >
                  {match.status}
                </span>
              </td>
              <td className="py-2.5 text-right text-[15px] text-shell">
                {(match.match_confidence * 100).toFixed(0)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-3 text-[13px] text-slate-tide">
        Matches are probabilistic — confidence is always shown, never certainty.
      </p>
    </section>
  );
}
