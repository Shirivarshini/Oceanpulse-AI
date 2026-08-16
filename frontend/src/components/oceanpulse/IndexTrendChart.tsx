import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ALERT_THRESHOLD } from "@/lib/oceanpulse/config";
import type { TimelinePoint } from "@/lib/oceanpulse/types";
import { Skeleton } from "./LoadingState";

interface TooltipPayloadItem {
  payload: TimelinePoint;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  const point = active ? payload?.[0]?.payload : undefined;
  if (!point) return null;

  return (
    <div className="rounded-[10px] border border-hairline-strong bg-elevated px-3 py-2 text-xs">
      <p className="font-display text-sm text-foreground">
        {point.label} &middot; Index {point.index}
      </p>
      <p className="mt-0.5 text-muted-foreground">{point.level}</p>
      {point.event && <p className="mt-1 max-w-48 text-muted-foreground">{point.event}</p>}
    </div>
  );
}

export function IndexTrendChart({
  timeline,
  loading,
}: {
  timeline: TimelinePoint[];
  loading: boolean;
}) {
  if (loading) return <Skeleton className="h-64 w-full" />;

  const crossing = timeline.find((p) => p.index >= ALERT_THRESHOLD);

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={timeline} margin={{ top: 12, right: 16, bottom: 4, left: -12 }}>
          <defs>
            <linearGradient id="gildedStroke" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="900" y2="0">
              <stop offset="0%" stopColor="var(--gilded-1)" />
              <stop offset="40%" stopColor="var(--gilded-2)" />
              <stop offset="70%" stopColor="var(--gilded-1)" />
              <stop offset="100%" stopColor="var(--gilded-2)" />
            </linearGradient>
            <linearGradient id="signalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--gilded-2)" stopOpacity={0.3} />
              <stop offset="55%" stopColor="var(--gilded-1)" stopOpacity={0.1} />
              <stop offset="100%" stopColor="var(--gilded-1)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--hairline)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
            stroke="var(--hairline)"
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
            stroke="var(--hairline)"
          />
          <Tooltip content={<ChartTooltip />} />
          <ReferenceLine
            y={ALERT_THRESHOLD}
            stroke="var(--hairline-strong)"
            strokeDasharray="4 4"
            label={{
              value: `Threshold ${ALERT_THRESHOLD}`,
              position: "insideTopRight",
              fill: "var(--muted-foreground)",
              fontSize: 11,
            }}
          />
          {crossing && (
            <ReferenceLine
              x={crossing.label}
              stroke="var(--hairline-strong)"
              label={{
                value: "Crossing",
                position: "insideBottomLeft",
                fill: "var(--muted-foreground)",
                fontSize: 10,
              }}
            />
          )}
          <Area
            type="monotone"
            dataKey="index"
            stroke="url(#gildedStroke)"
            strokeWidth={2}
            fill="url(#signalGradient)"
            dot={{ r: 3, fill: "var(--background)", stroke: "var(--gilded-2)", strokeWidth: 2 }}
            activeDot={{ r: 5 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
