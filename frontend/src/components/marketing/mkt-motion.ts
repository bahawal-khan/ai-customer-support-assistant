import { useReducedMotion } from "motion/react";
import type { Variants } from "motion/react";

/**
 * Single source of truth for scroll-reveal timing across every `.mkt` marketing section
 * (Hero, How It Works, Features & Capabilities). Import `useMktMotion()` instead of
 * hand-rolling variants per component so duration/ease/distance never drift between sections.
 *
 * The app root wraps everything in `<MotionConfig reducedMotion="user">` (see app/layout.tsx),
 * which is Framer Motion's own hydration-safe way of respecting prefers-reduced-motion: it
 * snaps transform/layout animations (our `y` slide) straight to their end value at animation
 * time while leaving opacity fades intact, giving the "simple fade, no slide" fallback for free.
 * Variant *shapes* below are intentionally NOT branched on `useReducedMotion()` — the hidden/show
 * values are what SSR renders as inline style, and a client-only reduced-motion check that reads
 * differently on the server vs. the first client render produces a React hydration mismatch.
 * Only non-rendered transition config (e.g. stagger timing) is safe to branch on it.
 */
export const MKT_MOTION = {
  duration: 0.5,
  ease: "easeOut" as const,
  y: 20,
  stagger: 0.1,
  delayChildren: 0.05,
};

export const MKT_VIEWPORT = { once: true, amount: 0.3 } as const;

export function useMktMotion() {
  const reduced = !!useReducedMotion();

  const item: Variants = {
    hidden: { opacity: 0, y: MKT_MOTION.y },
    show: { opacity: 1, y: 0, transition: { duration: MKT_MOTION.duration, ease: MKT_MOTION.ease } },
  };

  const container: Variants = {
    hidden: {},
    show: {
      transition: reduced
        ? { staggerChildren: 0 }
        : { staggerChildren: MKT_MOTION.stagger, delayChildren: MKT_MOTION.delayChildren },
    },
  };

  return { reduced, item, container, viewport: MKT_VIEWPORT };
}

/** Alternating violet/amber accent used by every card grid and step timeline in `.mkt`. */
export function mktAccentFor(index: number) {
  return index % 2 === 0 ? "var(--mkt-violet)" : "var(--mkt-amber)";
}
