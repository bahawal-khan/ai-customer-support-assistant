"use client";

import { motion, useReducedMotion } from "motion/react";
import { BookOpen, Bot, FileSearch, MessageSquareQuote, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { MKT_MOTION, mktAccentFor } from "@/components/marketing/mkt-motion";

const STAGES: { icon: LucideIcon; label: string; description: string }[] = [
  { icon: MessageSquareQuote, label: "Complaint", description: "Customer describes an issue" },
  { icon: Sparkles, label: "Intent · Sentiment · Priority", description: "DistilBERT classification" },
  { icon: BookOpen, label: "Knowledge Retrieval", description: "pgvector + LangChain search" },
  { icon: FileSearch, label: "Retrieved Sources", description: "Matching knowledge base passages" },
  { icon: Bot, label: "Grounded Response", description: "Generated via Groq" },
];

export function PipelinePreview() {
  const reduced = !!useReducedMotion();

  // Only transition *timing* (not rendered into SSR markup) branches on the client-only reduced
  // flag; MotionConfig(reducedMotion="user") in app/layout.tsx handles suppressing the scale/
  // scaleX/scaleY transform animations below for reduced-motion users. See mkt-motion.ts.
  const container = {
    hidden: {},
    show: {
      transition: reduced
        ? { staggerChildren: 0 }
        : { delayChildren: 0.25, staggerChildren: MKT_MOTION.stagger },
    },
  };

  const nodeVariants = {
    hidden: { opacity: 0, scale: 0.85 },
    show: { opacity: 1, scale: 1, transition: { duration: 0.32, ease: MKT_MOTION.ease } },
  };

  return (
    <div className="mkt relative w-full">
      {/* connecting line: vertical on mobile, horizontal from sm up */}
      <motion.div
        aria-hidden
        initial={{ scaleY: 0 }}
        animate={{ scaleY: 1 }}
        transition={{ duration: 0.7, ease: "easeInOut" }}
        style={{ transformOrigin: "top" }}
        className="absolute top-6 bottom-6 left-[21px] w-[2px] bg-gradient-to-b from-[var(--mkt-violet)] via-[var(--mkt-amber)] to-[var(--mkt-violet)] opacity-60 sm:hidden"
      />
      <motion.div
        aria-hidden
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.7, ease: "easeInOut" }}
        style={{ transformOrigin: "left" }}
        className="absolute top-1/2 right-6 left-6 hidden h-[2px] -translate-y-1/2 bg-gradient-to-r from-[var(--mkt-violet)] via-[var(--mkt-amber)] to-[var(--mkt-violet)] opacity-60 sm:block"
      />

      <motion.ol
        variants={container}
        initial="hidden"
        animate="show"
        className="relative flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between sm:gap-2"
      >
        {STAGES.map((stage, index) => {
          const accent = mktAccentFor(index);
          return (
            <motion.li
              key={stage.label}
              variants={nodeVariants}
              tabIndex={0}
              className="group relative z-10 flex flex-row items-center gap-3 rounded-lg p-1 outline-none sm:flex-1 sm:flex-col sm:items-center sm:gap-2 sm:text-center focus-visible:ring-2 focus-visible:ring-[var(--mkt-violet)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--mkt-bg)]"
            >
              <span
                className="flex size-11 shrink-0 items-center justify-center rounded-full border bg-[var(--mkt-surface)] text-[var(--mkt-text)] transition-transform duration-200 group-hover:scale-105"
                style={{ borderColor: `color-mix(in oklch, ${accent} 45%, transparent)`, boxShadow: `0 0 18px -6px ${accent}` }}
              >
                <stage.icon className="size-4" style={{ color: accent }} />
              </span>
              <div className="min-w-0">
                <p className="text-xs font-medium text-[var(--mkt-text)]">{stage.label}</p>
                <p className="mt-0.5 max-w-[10rem] text-[11px] leading-snug text-[var(--mkt-text-muted)] transition-opacity duration-200 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-visible:opacity-100">
                  {stage.description}
                </p>
              </div>
            </motion.li>
          );
        })}
      </motion.ol>
    </div>
  );
}
