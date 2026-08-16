import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Panel({
  title,
  subtitle,
  right,
  className,
  bodyClassName,
  children,
}: {
  title?: string;
  subtitle?: string;
  right?: ReactNode;
  className?: string;
  bodyClassName?: string;
  children: ReactNode;
}) {
  return (
    <section className={cn("tile flex flex-col", className)}>
      {(title || right) && (
        <header className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3 border-b border-hairline px-5 py-4">
          <div className="min-w-0">
            {title && (
              <h2 className="font-display text-xl leading-none text-foreground">{title}</h2>
            )}
            {subtitle && <p className="mt-1.5 text-xs text-muted-foreground">{subtitle}</p>}
          </div>
          {right}
        </header>
      )}
      <div className={cn("flex-1 px-5 py-4", bodyClassName)}>{children}</div>
    </section>
  );
}
