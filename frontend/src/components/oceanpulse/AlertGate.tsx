import { BellRing, BellOff, Clock, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AlertDecision, AlertGateResult } from "@/lib/oceanpulse/types";
import { Skeleton } from "./LoadingState";

type DecisionState = {
  label: string;
  text: string;
  border: string;
  bg: string;
  Icon: typeof BellRing;
  headline: string;
};

const DECISION: Record<AlertDecision, DecisionState> = {
  ALERT_DISPATCHED: {
    label: "ALERT_DISPATCHED",
    text: "text-critical",
    border: "border-critical/45",
    bg: "bg-critical/10",
    Icon: BellRing,
    headline: "Alert dispatched",
  },

  NO_ALERT: {
    label: "NO_ALERT",
    text: "text-accent",
    border: "border-accent/40",
    bg: "bg-accent/10",
    Icon: BellOff,
    headline: "No alert",
  },

  ALERT_BLOCKED_STALE: {
    label: "ALERT_BLOCKED_STALE",
    text: "text-signal-watch",
    border: "border-signal-watch/40",
    bg: "bg-signal-watch/10",
    Icon: Clock,
    headline: "Alert blocked — stale data",
  },
};

const FALLBACK_DECISION: DecisionState = {
  label: "NO_ALERT",
  text: "text-accent",
  border: "border-accent/40",
  bg: "bg-accent/10",
  Icon: BellOff,
  headline: "No alert",
};

/**
 * Runtime-safe alert decision lookup.
 *
 * TypeScript says alert.decision is AlertDecision, but API responses
 * can still contain malformed/missing values at runtime.
 */
function getDecisionState(decision: unknown): DecisionState {
  if (
    decision === "ALERT_DISPATCHED" ||
    decision === "NO_ALERT" ||
    decision === "ALERT_BLOCKED_STALE"
  ) {
    return DECISION[decision];
  }

  return FALLBACK_DECISION;
}

function getDecisionLabel(decision: unknown): string {
  if (
    decision === "ALERT_DISPATCHED" ||
    decision === "NO_ALERT" ||
    decision === "ALERT_BLOCKED_STALE"
  ) {
    return decision;
  }

  return "NO_ALERT";
}

export function AlertGate({
  alert,
  loading,
}: {
  alert: AlertGateResult | null;
  loading: boolean;
}) {
  if (loading || !alert) {
    return <Skeleton className="h-40 w-full" />;
  }

  const state = getDecisionState(alert.decision);
  const { Icon } = state;

  const threshold =
    typeof alert.threshold === "number" && Number.isFinite(alert.threshold)
      ? alert.threshold
      : 70;

  const index =
    typeof alert.index === "number" && Number.isFinite(alert.index)
      ? alert.index
      : 0;

  const over = index - threshold;

  const evaluatedAt =
    typeof alert.evaluated_at === "string" && alert.evaluated_at.length > 0
      ? alert.evaluated_at.slice(0, 10)
      : "—";

  const reason =
    typeof alert.reason === "string" && alert.reason.length > 0
      ? alert.reason
      : "No alert evaluation reason provided.";

  const decisionLabel = getDecisionLabel(alert.decision);

  return (
    <section className={cn("tile", state.border)}>
      <div
        className="hatch pointer-events-none absolute inset-y-0 right-0 w-40 opacity-40"
        aria-hidden
      />

      <header className="relative grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-hairline px-5 py-4">
        <div className="flex min-w-0 items-center gap-2.5">
          <ShieldAlert className={cn("size-4 shrink-0", state.text)} />

          <h2 className="font-display truncate text-xl leading-none text-foreground">
            Alert Gate — {state.headline}
          </h2>
        </div>

        <span className="label-caps shrink-0">
          Evaluated {evaluatedAt}
        </span>
      </header>

      <div className="relative grid gap-5 px-5 py-5 sm:grid-cols-2 lg:grid-cols-[repeat(3,minmax(0,auto))_minmax(0,1.4fr)] lg:items-center">
        {/* Threshold */}
        <div>
          <p className="label-caps">Threshold</p>

          <p className="font-display mt-1 text-4xl leading-none tabular-nums text-body">
            {threshold}
          </p>
        </div>

        {/* Current Index */}
        <div>
          <p className="label-caps">Current Index</p>

          <p
            className={cn(
              "font-display mt-1 text-4xl leading-none tabular-nums",
              state.text,
            )}
          >
            {index}

            <span className="ml-2 align-middle text-xs tracking-[0.1em] text-muted-foreground">
              {over >= 0 ? `+${over}` : over} vs gate
            </span>
          </p>
        </div>

        {/* Decision */}
        <div>
          <p className="label-caps">Decision</p>

          <span
            className={cn(
              "mt-2 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium tracking-[0.1em]",
              state.border,
              state.bg,
              state.text,
            )}
          >
            <Icon className="size-3.5" />

            {decisionLabel}
          </span>
        </div>

        {/* Reason */}
        <div className="border-hairline lg:border-l lg:pl-5">
          <p className="label-caps">Reason</p>

          <p className="mt-1.5 text-sm text-body">{reason}</p>
        </div>
      </div>
    </section>
  );
}