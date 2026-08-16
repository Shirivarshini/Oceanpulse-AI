import type { Alert } from "@/lib/oceanpulse/types";
import { AlertStatusBadge } from "./AlertStatusBadge";

export function AlertPanel({ alert }: { alert: Alert }) {
  return (
    <section className="rounded-[10px] bg-trench p-6">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-[15px] font-medium tracking-wide text-sea-fog uppercase">
          Alert gate
        </h3>
        <AlertStatusBadge status={alert.status} />
      </div>
      <p className="mt-3 text-[15px] text-shell">{alert.reason}</p>
      <p className="mt-2 text-[13px] text-slate-tide">Configured threshold · {alert.threshold}</p>
    </section>
  );
}
