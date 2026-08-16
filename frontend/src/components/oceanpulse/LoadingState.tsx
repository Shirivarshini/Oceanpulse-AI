import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-elevated", className)} />;
}

export function LoadingState({
  label = "Running analysis...",
  lines = 3,
  className,
}: {
  label?: string;
  lines?: number;
  className?: string;
}) {
  return (
    <div className={cn("space-y-3", className)} role="status" aria-live="polite">
      <p className="label-caps flex items-center gap-2">
        <span className="size-1.5 animate-pulse rounded-full bg-accent" />
        {label}
      </p>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className="h-4" />
      ))}
    </div>
  );
}
