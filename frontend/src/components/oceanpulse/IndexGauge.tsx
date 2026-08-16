import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { ALERT_THRESHOLD, LEVEL_STYLES } from "@/lib/oceanpulse/config";
import type { IndexLevel } from "@/lib/oceanpulse/types";

const SIZE = 240;
const R = 98;
const CX = SIZE / 2;
const CY = SIZE / 2;
/** 270° dial, opening at the bottom. */
const SWEEP = 270;
const START = 225;

function polar(angleDeg: number, radius = R) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: CX + radius * Math.cos(rad), y: CY + radius * Math.sin(rad) };
}

function arcPath(fromValue: number, toValue: number, radius = R) {
  const a0 = START + (fromValue / 100) * SWEEP;
  const a1 = START + (toValue / 100) * SWEEP;
  const p0 = polar(a0, radius);
  const p1 = polar(a1, radius);
  const large = a1 - a0 > 180 ? 1 : 0;
  return `M ${p0.x} ${p0.y} A ${radius} ${radius} 0 ${large} 1 ${p1.x} ${p1.y}`;
}

/** Radial instrument dial for the backend-provided ecosystem index. */
export function IndexGauge({
  index,
  level,
  className,
}: {
  index: number;
  level: IndexLevel;
  className?: string;
}) {
  const [shown, setShown] = useState(0);
  const style = LEVEL_STYLES[level];

  useEffect(() => {
    let frame = 0;
    const start = performance.now();
    const from = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / 900);
      const eased = 1 - Math.pow(1 - t, 3);
      setShown(Math.round(from + (index - from) * eased));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [index]);

  const thresholdPoint = polar(START + (ALERT_THRESHOLD / 100) * SWEEP, R + 9);
  const thresholdInner = polar(START + (ALERT_THRESHOLD / 100) * SWEEP, R - 9);

  return (
    <div className={cn("relative mx-auto w-full max-w-[240px]", className)}>
      <svg
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="w-full"
        role="img"
        aria-label={`Ecosystem index ${index} of 100, level ${level}`}
      >
        <defs>
          <linearGradient id="gaugeGilded" gradientUnits="userSpaceOnUse" x1="20" y1="220" x2="220" y2="20">
            <stop offset="0%" stopColor="var(--gilded-1)" />
            <stop offset="55%" stopColor="var(--gilded-2)" />
            <stop offset="100%" stopColor="var(--gilded-1)" />
          </linearGradient>
        </defs>

        {/* track */}
        <path
          d={arcPath(0, 100)}
          fill="none"
          stroke="var(--hairline)"
          strokeWidth={10}
          strokeLinecap="round"
        />

        {/* ticks every 10 */}
        {Array.from({ length: 11 }).map((_, i) => {
          const a = START + (i * 10 * SWEEP) / 100;
          const outer = polar(a, R - 10);
          const inner = polar(a, i % 5 === 0 ? R - 20 : R - 16);
          return (
            <line
              key={i}
              x1={outer.x}
              y1={outer.y}
              x2={inner.x}
              y2={inner.y}
              stroke="var(--hairline-strong)"
              strokeWidth={i % 5 === 0 ? 1.4 : 0.8}
            />
          );
        })}

        {/* value arc */}
        <path
          d={arcPath(0, Math.max(0.5, shown))}
          fill="none"
          stroke="url(#gaugeGilded)"
          strokeWidth={10}
          strokeLinecap="round"
        />

        {/* alert threshold marker */}
        <line
          x1={thresholdInner.x}
          y1={thresholdInner.y}
          x2={thresholdPoint.x}
          y2={thresholdPoint.y}
          stroke="var(--foreground)"
          strokeWidth={1.5}
        />
      </svg>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center pt-2">
        <span
          className={cn(
            "font-display text-[68px] leading-none tabular-nums",
            style.text,
          )}
        >
          {shown}
        </span>
        <span className="mt-1 text-[10px] tracking-[0.22em] text-muted-foreground">
          / 100 INDEX
        </span>
      </div>

      <p className="mt-1 text-center text-[10px] tracking-[0.16em] text-muted-foreground">
        ALERT THRESHOLD {ALERT_THRESHOLD}
      </p>
    </div>
  );
}
