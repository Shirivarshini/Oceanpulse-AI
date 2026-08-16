import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TimelinePoint } from "@/lib/oceanpulse/types";

function shortDate(ts: string) {
  return new Date(ts).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function TrendChart({ timeline }: { timeline: TimelinePoint[] }) {
  const data = timeline.map((point) => ({ ...point, label: shortDate(point.timestamp) }));

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
          <defs>
            <linearGradient id="signal-line" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="700" y2="0">
              <stop offset="0%" stopColor="rgb(63,216,201)" />
              <stop offset="40%" stopColor="rgb(210,255,248)" />
              <stop offset="70%" stopColor="rgb(63,216,201)" />
            </linearGradient>
            <linearGradient id="signal-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgb(63,216,201)" stopOpacity={0.22} />
              <stop offset="100%" stopColor="rgb(63,216,201)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1a2530" vertical={false} />
          <XAxis
            dataKey="label"
            stroke="#455a6b"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#7690a3", fontSize: 12 }}
          />
          <YAxis
            domain={[0, 100]}
            stroke="#455a6b"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#7690a3", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ stroke: "#2b3a48" }}
            contentStyle={{
              background: "#101821",
              border: "1px solid #1a2530",
              borderRadius: 10,
              color: "#e3ebf0",
              fontSize: 13,
            }}
            labelStyle={{ color: "#93aabb" }}
            formatter={(value: number, _n, item) => [
              `${value} · ${(item?.payload as TimelinePoint)?.event ?? ""}`,
              "Index",
            ]}
          />
          <Area
            type="monotone"
            dataKey="index"
            stroke="url(#signal-line)"
            strokeWidth={2}
            fill="url(#signal-fill)"
            dot={{ r: 3, fill: "#3fd8c9", strokeWidth: 0 }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
