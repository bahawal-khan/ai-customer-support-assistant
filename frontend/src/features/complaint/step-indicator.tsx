import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

const STEPS = ["Describe", "Analyze", "Results"] as const;

export type ComplaintStep = 0 | 1 | 2;

export function StepIndicator({ current }: { current: ComplaintStep }) {
  return (
    <ol className="flex items-center gap-2 sm:gap-4">
      {STEPS.map((label, index) => {
        const stepIndex = index as ComplaintStep;
        const isDone = stepIndex < current;
        const isActive = stepIndex === current;

        return (
          <li key={label} className="flex flex-1 items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "flex size-7 shrink-0 items-center justify-center rounded-full border text-xs font-medium transition-colors",
                  isDone && "border-primary bg-primary text-primary-foreground",
                  isActive && "border-primary text-primary",
                  !isDone && !isActive && "border-border text-muted-foreground"
                )}
              >
                {isDone ? <Check className="size-3.5" /> : index + 1}
              </span>
              <span
                className={cn(
                  "hidden text-sm font-medium sm:inline",
                  isActive || isDone ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div className={cn("h-px flex-1", isDone ? "bg-primary" : "bg-border")} />
            )}
          </li>
        );
      })}
    </ol>
  );
}
