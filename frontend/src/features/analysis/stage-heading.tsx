import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

export function StageHeading({
  step,
  label,
  icon: Icon,
  className,
}: {
  step: number;
  label: string;
  icon?: LucideIcon;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full border border-border text-xs font-medium text-muted-foreground">
        {step}
      </span>
      {Icon ? <Icon className="size-4 text-muted-foreground" /> : null}
      <span className="text-sm font-medium text-foreground">{label}</span>
    </div>
  );
}
