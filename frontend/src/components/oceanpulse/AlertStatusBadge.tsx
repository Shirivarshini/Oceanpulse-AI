import { AlertTriangle, ShieldCheck, Clock } from "lucide-react";
import type { AlertStatus } from "@/lib/oceanpulse/types";
import { cn } from "@/lib/utils";

const CONFIG: Record<AlertStatus, { label: string; className: string; Icon: typeof AlertTriangle }> =
  {
    NO_ALERT: { label: "No alert", className: "border-sage text-sage", Icon: ShieldCheck },
    ALERT_DISPATCHED: {
      label: "Alert dispatched",
      className: "border-coral-alert text-coral-alert",
      Icon: AlertTriangle,
    },
    ALERT_BLOCKED_STALE: {
      label: "Alert blocked · stale",
      className: "border-tide-current text-sea-fog",
      Icon: Clock,
    },
  };

export function AlertStatusBadge({
  status,
  className,
}: {
  status: AlertStatus;
  className?: string;
}) {
  const { label, className: tone, Icon } = CONFIG[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-0.5 text-[12px] font-medium",
        tone,
        className,
      )}
    >
      <Icon className="size-3.5" strokeWidth={1.5} />
      {label}
    </span>
  );
}
