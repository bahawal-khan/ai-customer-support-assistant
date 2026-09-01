"use client";

import * as React from "react";
import { motion } from "motion/react";
import { Link2, ListChecks, ShieldCheck, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useMktMotion, mktAccentFor } from "@/components/marketing/mkt-motion";

const BENEFITS: { icon: LucideIcon; title: string; description: string }[] = [
  {
    icon: ShieldCheck,
    title: "Grounded, not invented",
    description:
      "Policy claims in a generated response come only from your indexed knowledge base articles, never from the model's general knowledge.",
  },
  {
    icon: ListChecks,
    title: "The same triage every time",
    description:
      "Priority is set by a fixed rule based on intent and sentiment, so two similar complaints are never triaged inconsistently.",
  },
  {
    icon: Zap,
    title: "A draft the moment it's submitted",
    description:
      "Classification, retrieval, and response generation all run automatically as part of the same request — no manual lookup first.",
  },
  {
    icon: Link2,
    title: "Every claim is traceable",
    description:
      "The retrieved source passages behind a response are returned and displayed alongside it, so any claim can be checked against the original document.",
  },
];

export function WhyUseIt() {
  const { item, container } = useMktMotion();

  return (
    <section
      id="why-use-it"
      className="mkt relative scroll-mt-14 overflow-hidden border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] py-20 text-[var(--mkt-text)] sm:py-28"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 right-1/4 size-80 -translate-y-1/2 rounded-full opacity-[0.1] blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-amber)" }}
      />

      <div className="content-container relative flex flex-col gap-16 sm:gap-20">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          variants={item}
          className="mx-auto flex max-w-2xl flex-col items-center gap-4 text-center"
        >
          <div className="flex items-center gap-2 text-xs font-medium tracking-[0.14em] text-[var(--mkt-text-muted)] uppercase">
            <span className="size-1.5 rounded-full" style={{ background: "var(--mkt-amber)" }} />
            Why use it
          </div>
          <h2 className="font-display text-[clamp(2rem,4vw,3rem)] leading-[1.1] tracking-[-0.02em] text-balance">
            Built to be trusted, not just fast
          </h2>
          <p className="max-w-lg text-base leading-relaxed text-[var(--mkt-text-muted)] sm:text-lg">
            The same properties that make the pipeline demoable above are what make it safe to
            rely on.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.2 }}
          variants={container}
          className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          {BENEFITS.map((benefit, index) => {
            const accent = mktAccentFor(index);
            return (
              <motion.div
                key={benefit.title}
                variants={item}
                className="mkt-card flex flex-col gap-4 rounded-2xl border p-6 shadow-sm"
                style={{ "--mkt-accent": accent } as React.CSSProperties}
              >
                <span
                  className="flex size-10 shrink-0 items-center justify-center rounded-full"
                  style={{ background: `color-mix(in oklch, ${accent} 16%, transparent)` }}
                >
                  <benefit.icon className="size-5" style={{ color: accent }} />
                </span>
                <div>
                  <h3 className="font-heading text-base font-semibold text-[var(--mkt-text)]">
                    {benefit.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-[var(--mkt-text-muted)]">
                    {benefit.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
