"use client";

import * as React from "react";
import { motion, useReducedMotion } from "motion/react";
import { Check, Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

/**
 * docs/design/ANIMATION_SPEC.md "Complaint analysis": do not fake a
 * percentage, animate discrete stages sequentially. Stage transitions are
 * driven by real elapsed time since the actual request started (not a fixed
 * per-step timer) so a fast response advances through fewer visible stages
 * instead of forcing a minimum wait. The caller navigates away the instant
 * the real request resolves — this component never blocks that.
 */
const STAGES = [
  "Analyzing complaint...",
  "Classifying intent & sentiment...",
  "Retrieving relevant knowledge...",
  "Generating response...",
] as const;

const STAGE_THRESHOLDS_MS = [0, 500, 1100, 2000];

export function PipelineStages() {
  const [activeIndex, setActiveIndex] = React.useState(0);
  const prefersReducedMotion = useReducedMotion();

  React.useEffect(() => {
    if (prefersReducedMotion) return;
    const start = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - start;
      const crossed = STAGE_THRESHOLDS_MS.filter((t) => elapsed >= t).length - 1;
      setActiveIndex(Math.min(Math.max(crossed, 0), STAGES.length - 1));
    }, 150);
    return () => clearInterval(interval);
  }, [prefersReducedMotion]);

  return (
    <ul className="space-y-3">
      {STAGES.map((label, index) => {
        const isDone = index < activeIndex;
        const isActive = index === activeIndex;

        return (
          <motion.li
            key={label}
            initial={prefersReducedMotion ? false : { opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: prefersReducedMotion ? 0 : index * 0.03 }}
            className="flex items-center gap-3"
          >
            <span
              className={cn(
                "flex size-6 shrink-0 items-center justify-center rounded-full border text-xs",
                isDone && "border-success bg-success/10 text-success",
                isActive && "border-primary text-primary",
                !isDone && !isActive && "border-border text-muted-foreground"
              )}
            >
              {isDone ? (
                <Check className="size-3.5" />
              ) : isActive ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <span className="size-1.5 rounded-full bg-current" />
              )}
            </span>
            <span
              className={cn(
                "text-sm",
                isDone || isActive ? "text-foreground" : "text-muted-foreground"
              )}
            >
              {label}
            </span>
          </motion.li>
        );
      })}
    </ul>
  );
}
