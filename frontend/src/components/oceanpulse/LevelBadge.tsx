import type { IndexLevel } from "@/lib/oceanpulse/types";
import { cn } from "@/lib/utils";

const TONE: Record<IndexLevel, string> = {
  STABLE: "border-bioluminescence text-bioluminescence",
  WATCH: "border-mist-spray text-mist-spray",
  STRESSED: "border-coral-alert text-coral-alert",
  CRITICAL: "border-coral-alert text-coral-alert",
};

export function LevelBadge({ level, className }: { level: IndexLevel; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-0.5 text-[12px] font-medium tracking-wide uppercase",
        TONE[level],
        className,
      )}
    >
      {level.toLowerCase()}
    </span>
  );
}
