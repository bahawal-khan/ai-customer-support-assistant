"use client";

import * as React from "react";
import { motion, useScroll, useTransform } from "motion/react";
import type { MotionValue, Variants } from "motion/react";
import { Bot, BookOpen, Database, MessageSquareQuote, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useMktMotion, mktAccentFor } from "@/components/marketing/mkt-motion";

const TAGS = ["Billing", "Duplicate charge", "Urgent"];

const ATTRIBUTES = [
  { label: "Intent", value: "Payment issue" },
  { label: "Sentiment", value: "Negative" },
  { label: "Priority", value: "High" },
];

const SOURCES = [
  {
    title: "Payment FAQ",
    category: "Payment",
    match: 96,
    snippet:
      "Duplicate charges are flagged automatically once a second authorization is detected on the same order.",
  },
  {
    title: "Refund Policy",
    category: "Refund",
    match: 91,
    snippet: "Confirmed duplicate charges are reversed to the original payment method.",
  },
  {
    title: "Escalation Policy",
    category: "Escalation",
    match: 84,
    snippet: "Billing issues marked high priority are routed to a human agent for review.",
  },
];

const STEP_COUNT = 5;

/** number is 1-indexed (Step 1..5); alternate starting on violet. */
function accentFor(number: number) {
  return mktAccentFor(number - 1);
}

export function HowItWorks() {
  const { item } = useMktMotion();
  const timelineRef = React.useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: timelineRef,
    offset: ["start 0.8", "end 0.35"],
  });

  return (
    <section
      id="how-it-works"
      className="mkt relative scroll-mt-14 overflow-hidden border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] py-20 text-[var(--mkt-text)] sm:py-28"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute top-1/3 right-0 size-96 -translate-y-1/2 rounded-full opacity-[0.12] blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-violet)" }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute bottom-0 left-0 size-80 rounded-full opacity-[0.1] blur-3xl motion-reduce:hidden"
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
            How it works
          </div>
          <h2 className="font-display text-[clamp(2rem,4vw,3rem)] leading-[1.1] tracking-[-0.02em] text-balance">
            From raw complaint to a grounded answer
          </h2>
          <p className="max-w-lg text-base leading-relaxed text-[var(--mkt-text-muted)] sm:text-lg">
            Every card below reflects the same pipeline your complaints run through — nothing here
            is staged.
          </p>
        </motion.div>

        <div ref={timelineRef} className="relative mx-auto flex w-full max-w-5xl flex-col gap-20 sm:gap-28">
          <div
            aria-hidden
            className="absolute top-2 bottom-2 left-[19px] w-[2px] overflow-hidden rounded-full bg-[var(--mkt-text-muted)]/12 sm:left-[23px]"
          >
            <motion.div
              className="w-full origin-top bg-gradient-to-b from-[var(--mkt-violet)] via-[var(--mkt-amber)] to-[var(--mkt-violet)]"
              style={{ height: "100%", scaleY: scrollYProgress }}
            />
          </div>

          <StepRow
            index={0}
            icon={MessageSquareQuote}
            title="Complaint comes in"
            description="The customer describes the issue in their own words; auto-tags are applied the moment it's submitted."
            scrollYProgress={scrollYProgress}
            item={item}
          >
            {(accent) => (
              <div
                className="mkt-card rounded-2xl rounded-bl-md border p-5 shadow-sm sm:p-6"
                style={{ "--mkt-accent": accent } as React.CSSProperties}
              >
                <div className="mb-3 flex items-center gap-2">
                  <span className="size-1.5 rounded-full bg-[var(--mkt-text-muted)]/50" />
                  <span className="text-xs font-medium tracking-[0.06em] text-[var(--mkt-text-muted)] uppercase">
                    Customer complaint
                  </span>
                </div>
                <p className="rounded-xl rounded-bl-sm border border-[var(--mkt-text-muted)]/12 bg-[var(--mkt-bg)] p-3.5 text-sm leading-relaxed text-[var(--mkt-text)]">
                  &ldquo;I was charged twice for the same order and need this fixed.&rdquo;
                </p>
                <p className="mt-4 mb-2 text-xs font-medium tracking-[0.08em] text-[var(--mkt-text-muted)] uppercase">
                  Auto-tags
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAGS.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border px-2.5 py-1 text-xs font-medium text-[var(--mkt-text)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_6px_16px_-8px_var(--mkt-violet)]"
                      style={{
                        borderColor: "color-mix(in oklch, var(--mkt-violet) 35%, transparent)",
                        background: "color-mix(in oklch, var(--mkt-violet) 10%, transparent)",
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </StepRow>

          <StepRow
            index={1}
            icon={Sparkles}
            title="Intent, sentiment & priority"
            description="A DistilBERT classifier reads the complaint to determine what the customer wants and how urgent it is."
            scrollYProgress={scrollYProgress}
            item={item}
          >
            {(accent) => (
              <div
                className="mkt-card rounded-2xl border p-5 shadow-sm sm:p-6"
                style={{ "--mkt-accent": accent } as React.CSSProperties}
              >
                <dl className="flex flex-col divide-y divide-[var(--mkt-text-muted)]/10">
                  {ATTRIBUTES.map((attr) => (
                    <div
                      key={attr.label}
                      className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
                    >
                      <dt className="text-sm text-[var(--mkt-text-muted)]">{attr.label}</dt>
                      <dd
                        className="rounded-full border px-2.5 py-1 text-xs font-semibold"
                        style={{
                          color: "var(--mkt-text)",
                          borderColor: "color-mix(in oklch, var(--mkt-amber) 35%, transparent)",
                          background: "color-mix(in oklch, var(--mkt-amber) 10%, transparent)",
                        }}
                      >
                        {attr.value}
                      </dd>
                    </div>
                  ))}
                </dl>
                <p className="mt-3 text-xs leading-relaxed text-[var(--mkt-text-muted)]">
                  Negative sentiment on a sensitive intent (payment_issue).
                </p>
              </div>
            )}
          </StepRow>

          <StepRow
            index={2}
            icon={BookOpen}
            title="Knowledge retrieval"
            description="pgvector and LangChain search the knowledge base and surface the passages closest to the complaint."
            scrollYProgress={scrollYProgress}
            item={item}
          >
            {(accent) => (
              <div className="flex flex-col gap-3">
                {SOURCES.map((source) => (
                  <div
                    key={source.title}
                    className="mkt-card flex items-start gap-3 rounded-xl border p-4 shadow-sm"
                    style={{ "--mkt-accent": accent } as React.CSSProperties}
                  >
                    <MatchRing score={source.match} />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                        <span className="text-sm font-semibold text-[var(--mkt-text)]">
                          {source.title}
                        </span>
                        <span className="text-[11px] font-medium tracking-[0.06em] text-[var(--mkt-text-muted)] uppercase">
                          {source.category}
                        </span>
                      </div>
                      <p className="mt-1 text-sm leading-relaxed text-[var(--mkt-text-muted)]">
                        {source.snippet}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </StepRow>

          <StepRow
            index={3}
            icon={Database}
            title="Knowledge base coverage"
            description="Retrieval draws from the same indexed articles behind every response."
            scrollYProgress={scrollYProgress}
            item={item}
          >
            {(accent) => (
              <div
                className="mkt-card flex flex-col gap-5 rounded-2xl border p-5 shadow-sm sm:flex-row sm:p-6"
                style={{ "--mkt-accent": accent } as React.CSSProperties}
              >
                <div className="flex-1">
                  <p className="font-display text-3xl" style={{ color: accent }}>
                    9
                  </p>
                  <p className="mt-1 text-sm text-[var(--mkt-text-muted)]">
                    Knowledge base articles indexed
                  </p>
                </div>
                <div className="flex-1 border-t border-[var(--mkt-text-muted)]/10 pt-4 sm:border-t-0 sm:border-l sm:pt-0 sm:pl-6">
                  <p className="text-sm font-semibold text-[var(--mkt-text)]">pgvector + LangChain</p>
                  <p className="mt-1 text-sm text-[var(--mkt-text-muted)]">
                    Semantic retrieval over embedded passages
                  </p>
                </div>
              </div>
            )}
          </StepRow>

          <StepRow
            index={4}
            icon={Bot}
            title="Grounded response"
            description="Groq drafts a reply that cites the retrieved sources directly — nothing invented."
            scrollYProgress={scrollYProgress}
            item={item}
          >
            {(accent) => (
              <div
                className="mkt-card mkt-card--emphasis rounded-2xl border-2 p-6 shadow-md sm:p-8"
                style={{ "--mkt-accent": accent } as React.CSSProperties}
              >
                <div className="mb-3 flex items-center gap-2">
                  <span
                    className="flex size-6 items-center justify-center rounded-full"
                    style={{ background: `color-mix(in oklch, ${accent} 18%, transparent)` }}
                  >
                    <Bot className="size-3.5" style={{ color: accent }} />
                  </span>
                  <span className="text-xs font-medium tracking-[0.06em] text-[var(--mkt-text-muted)] uppercase">
                    Generated reply
                  </span>
                </div>
                <p className="text-base leading-relaxed text-[var(--mkt-text)]">
                  Thanks for flagging this — I can see two charges on the same order. Duplicate
                  charges like this are reviewed automatically and reversed to your original payment
                  method once confirmed
                  <sup className="mx-0.5 font-semibold" style={{ color: accent }}>
                    [1]
                  </sup>
                  <sup className="mx-0.5 font-semibold" style={{ color: accent }}>
                    [2]
                  </sup>
                  . Given the billing impact, I&apos;ve marked this high priority.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--mkt-text-muted)]/10 pt-4">
                  <span
                    className="rounded-full border px-2.5 py-1 text-xs font-medium text-[var(--mkt-text-muted)]"
                    style={{ borderColor: "color-mix(in oklch, var(--mkt-text-muted) 25%, transparent)" }}
                  >
                    [1] Payment FAQ
                  </span>
                  <span
                    className="rounded-full border px-2.5 py-1 text-xs font-medium text-[var(--mkt-text-muted)]"
                    style={{ borderColor: "color-mix(in oklch, var(--mkt-text-muted) 25%, transparent)" }}
                  >
                    [2] Refund Policy
                  </span>
                </div>
              </div>
            )}
          </StepRow>
        </div>
      </div>
    </section>
  );
}

function MatchRing({ score }: { score: number }) {
  const accent = score >= 90 ? "var(--mkt-violet)" : "var(--mkt-amber)";
  const radius = 15;
  const circumference = 2 * Math.PI * radius;
  const dash = (score / 100) * circumference;

  return (
    <span className="relative inline-flex size-10 shrink-0 items-center justify-center" aria-hidden>
      <svg viewBox="0 0 36 36" className="size-10 -rotate-90">
        <circle
          cx="18"
          cy="18"
          r={radius}
          fill="none"
          strokeWidth="3"
          className="stroke-[var(--mkt-text-muted)]/15"
        />
        <circle
          cx="18"
          cy="18"
          r={radius}
          fill="none"
          strokeWidth="3"
          strokeLinecap="round"
          stroke={accent}
          strokeDasharray={`${dash} ${circumference}`}
        />
      </svg>
      <span className="absolute text-[9px] font-semibold" style={{ color: accent }}>
        {score}
      </span>
    </span>
  );
}

function StepRow({
  index,
  icon: Icon,
  title,
  description,
  children,
  scrollYProgress,
  item,
}: {
  index: number;
  icon: LucideIcon;
  title: string;
  description: string;
  children: (accent: string) => React.ReactNode;
  scrollYProgress: MotionValue<number>;
  item: Variants;
}) {
  const number = index + 1;
  const accent = accentFor(number);
  const pos = index / (STEP_COUNT - 1);
  const glow = useTransform(scrollYProgress, [Math.max(0, pos - 0.12), Math.min(1, pos + 0.02)], [0.15, 1], {
    clamp: true,
  });

  return (
    <div className="relative flex gap-5 sm:gap-8">
      <div className="relative z-10 shrink-0">
        <span
          className="relative flex size-10 items-center justify-center rounded-full border bg-[var(--mkt-bg)] sm:size-12"
          style={{ borderColor: "color-mix(in oklch, var(--mkt-text-muted) 25%, transparent)" }}
        >
          <motion.span
            aria-hidden
            className="absolute inset-0 rounded-full border"
            style={{
              borderColor: accent,
              boxShadow: `0 0 20px 1px ${accent}`,
              opacity: glow,
            }}
          />
          <Icon className="relative z-10 size-4 sm:size-5" style={{ color: accent }} />
        </span>
      </div>

      <motion.div
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, amount: 0.3 }}
        variants={item}
        className="flex min-w-0 flex-1 flex-col gap-5 sm:flex-row sm:items-center sm:gap-8 lg:gap-12"
      >
        <div className="sm:w-[34%] sm:shrink-0">
          <p className="text-xs font-semibold tracking-[0.1em] uppercase" style={{ color: accent }}>
            Step {number}
          </p>
          <h3 className="font-heading mt-1 text-xl font-semibold text-[var(--mkt-text)] sm:text-2xl">
            {title}
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-[var(--mkt-text-muted)]">{description}</p>
        </div>
        <div className="min-w-0 flex-1">{children(accent)}</div>
      </motion.div>
    </div>
  );
}
