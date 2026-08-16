import { MapPin } from "lucide-react";
import type { Region } from "@/lib/oceanpulse/types";

export function RegionSelector({
  regions,
  value,
  onChange,
}: {
  regions: Region[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <label className="block">
      <span className="label-caps">Region</span>
      <div className="mt-2 flex items-center gap-2 rounded-[10px] border border-hairline bg-elevated px-3 py-2">
        <MapPin className="size-4 text-accent" />
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-transparent text-sm text-body outline-none"
        >
          {regions.map((r) => (
            <option key={r.id} value={r.id} className="bg-elevated text-body">
              {r.name}
            </option>
          ))}
        </select>
      </div>
    </label>
  );
}
