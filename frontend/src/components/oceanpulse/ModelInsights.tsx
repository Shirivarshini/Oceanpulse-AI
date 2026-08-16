import { Brain } from "lucide-react";
import { Panel } from "./Panel";

const SLOTS = [
  { label: "Forecast (7-day index)", note: "Awaiting model endpoint" },
  { label: "Anomaly score", note: "Awaiting model endpoint" },
  { label: "Model confidence", note: "Awaiting model endpoint" },
];

/**
 * Forward-compatible surface for future ML outputs. Renders explicit
 * "not connected" states — never fabricated model values.
 */
export function ModelInsights() {
  return (
    <Panel
      title="Predictive Layer"
      subtitle="Reserved for ML forecasts once the model endpoint is connected."
      right={
        <span className="inline-flex items-center gap-1.5 rounded-full border border-hairline-strong bg-elevated/60 px-2.5 py-0.5 text-[10px] font-medium tracking-[0.14em] text-muted-foreground">
          <span className="size-1.5 rounded-full bg-current" />
          NOT CONNECTED
        </span>
      }
      bodyClassName="space-y-3"
    >
      {SLOTS.map((slot) => (
        <div
          key={slot.label}
          className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 rounded-[10px] border border-dashed border-hairline-strong/70 px-3 py-2.5"
        >
          <span className="flex min-w-0 items-center gap-2 text-sm text-muted-foreground">
            <Brain className="size-3.5 shrink-0 text-accent" />
            <span>{slot.label}</span>
          </span>
          <span className="shrink-0 text-[10px] tracking-[0.14em] text-muted-foreground">
            {slot.note.toUpperCase()}
          </span>
        </div>
      ))}
      <p className="text-xs text-muted-foreground">
        No model output is displayed until the analysis API returns it. Nothing here is inferred in
        the browser.
      </p>
    </Panel>
  );
}
