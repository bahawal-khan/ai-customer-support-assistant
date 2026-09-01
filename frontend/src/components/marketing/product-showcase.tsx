"use client";

import * as React from "react";
import { AnimatePresence, motion } from "motion/react";
import { Bot, BookOpen, MessageSquareQuote, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useMktMotion } from "@/components/marketing/mkt-motion";
import { MAX_COMPLAINT_LENGTH } from "@/lib/constants";

const COMPLAINT_TEXT = "I was charged twice for the same order and need this fixed.";

/** Mirrors backend/tests/test_api_complaints.py `_result()` fixture — the same canonical
 * "charged twice" example whose priority reason string is already reused verbatim in
 * How It Works, so its intent/sentiment confidence values are treated as real here too. */
const ANALYSIS_ATTRIBUTES = [
  { label: "Intent", value: "Payment issue", confidence: 0.97 },
  { label: "Sentiment", value: "Negative", confidence: 0.88 },
];

const PRIORITY = {
  level: "High",
  reason: "Negative sentiment on a sensitive intent (payment_issue).",
};

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

const CITATIONS = [
  { mark: "[1]", label: "Payment FAQ" },
  { mark: "[2]", label: "Refund Policy" },
];

type TabId = "complaint" | "analysis" | "sources" | "response";

const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: "complaint", label: "New Complaint", icon: MessageSquareQuote },
  { id: "analysis", label: "Analysis Results", icon: Sparkles },
  { id: "sources", label: "Retrieved Sources", icon: BookOpen },
  { id: "response", label: "AI Response", icon: Bot },
];

export function ProductShowcase() {
  const { item } = useMktMotion();
  const [activeTab, setActiveTab] = React.useState<TabId>("complaint");

  return (
    <section
      id="product-showcase"
      className="mkt relative scroll-mt-14 overflow-hidden border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] py-20 text-[var(--mkt-text)] sm:py-28"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 size-96 -translate-x-1/2 -translate-y-1/2 rounded-full opacity-[0.1] blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-violet)" }}
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
            <span className="size-1.5 rounded-full" style={{ background: "var(--mkt-violet)" }} />
            Product showcase
          </div>
          <h2 className="font-display text-[clamp(2rem,4vw,3rem)] leading-[1.1] tracking-[-0.02em] text-balance">
            See it in action
          </h2>
          <p className="max-w-lg text-base leading-relaxed text-[var(--mkt-text-muted)] sm:text-lg">
            One live product, four moments in the same pipeline. Switch tabs to jump straight to
            any screen.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.97, y: 16 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="mkt-card mx-auto w-full max-w-4xl overflow-hidden rounded-3xl border shadow-md"
          style={{ "--mkt-accent": "var(--mkt-violet)" } as React.CSSProperties}
        >
          <div className="flex flex-col gap-3 border-b border-[var(--mkt-text-muted)]/10 px-4 pt-4 sm:px-6 sm:pt-5">
            <div aria-hidden className="flex items-center gap-1.5">
              <span className="size-2.5 rounded-full bg-[var(--mkt-text-muted)]/25" />
              <span className="size-2.5 rounded-full bg-[var(--mkt-text-muted)]/25" />
              <span className="size-2.5 rounded-full bg-[var(--mkt-text-muted)]/25" />
            </div>

            <div role="tablist" aria-label="Product showcase screens" className="flex flex-wrap gap-1 sm:gap-2">
              {TABS.map((tab) => {
                const active = tab.id === activeTab;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    role="tab"
                    aria-selected={active}
                    onClick={() => setActiveTab(tab.id)}
                    className="relative flex items-center gap-1.5 rounded-t-lg px-3 py-2.5 text-xs font-medium transition-colors duration-200 sm:text-sm"
                    style={{
                      color: active ? "var(--mkt-text)" : "var(--mkt-text-muted)",
                    }}
                  >
                    <tab.icon className="size-3.5 shrink-0 sm:size-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                    {active && (
                      <motion.span
                        layoutId="mkt-showcase-tab-underline"
                        className="absolute inset-x-2 -bottom-px h-[2px] rounded-full"
                        style={{ background: "var(--mkt-violet)" }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="relative min-h-[26rem] overflow-hidden p-5 sm:min-h-[24rem] sm:p-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
              >
                {activeTab === "complaint" && <ComplaintScreen />}
                {activeTab === "analysis" && <AnalysisScreen />}
                {activeTab === "sources" && <SourcesScreen />}
                {activeTab === "response" && <ResponseScreen />}
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function ComplaintScreen() {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <p className="text-sm font-semibold text-[var(--mkt-text)]">Describe the issue</p>
        <p className="mt-1 text-xs text-[var(--mkt-text-muted)]">
          Describe the issue in your own words — our AI will classify it and find a grounded
          answer.
        </p>
      </div>
      <div className="rounded-xl border border-[var(--mkt-text-muted)]/15 bg-[var(--mkt-bg)] p-4">
        <p className="text-sm leading-relaxed text-[var(--mkt-text)]">{COMPLAINT_TEXT}</p>
      </div>
      <div className="flex justify-end text-xs text-[var(--mkt-text-muted)]">
        {COMPLAINT_TEXT.length}/{MAX_COMPLAINT_LENGTH}
      </div>
      <button
        type="button"
        className="mkt-card flex w-full items-center justify-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium text-[var(--mkt-text)] shadow-sm"
        style={{ "--mkt-accent": "var(--mkt-violet)" } as React.CSSProperties}
      >
        <Sparkles className="size-4" style={{ color: "var(--mkt-violet)" }} />
        Analyze Complaint
      </button>
    </div>
  );
}

function AnalysisScreen() {
  return (
    <div className="flex flex-col gap-5">
      <dl className="flex flex-col divide-y divide-[var(--mkt-text-muted)]/10">
        {ANALYSIS_ATTRIBUTES.map((attr) => (
          <div key={attr.label} className="flex items-center justify-between gap-4 py-3 first:pt-0">
            <dt className="text-sm text-[var(--mkt-text-muted)]">{attr.label}</dt>
            <div className="flex items-center gap-2">
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
              <span className="text-xs font-medium text-[var(--mkt-text-muted)]">
                {Math.round(attr.confidence * 100)}% confidence
              </span>
            </div>
          </div>
        ))}
        <div className="flex items-center justify-between gap-4 py-3 last:pb-0">
          <dt className="text-sm text-[var(--mkt-text-muted)]">Priority</dt>
          <dd
            className="rounded-full border px-2.5 py-1 text-xs font-semibold"
            style={{
              color: "var(--mkt-text)",
              borderColor: "color-mix(in oklch, var(--mkt-violet) 35%, transparent)",
              background: "color-mix(in oklch, var(--mkt-violet) 10%, transparent)",
            }}
          >
            {PRIORITY.level}
          </dd>
        </div>
      </dl>
      <p className="text-xs leading-relaxed text-[var(--mkt-text-muted)]">{PRIORITY.reason}</p>
    </div>
  );
}

function SourcesScreen() {
  return (
    <div className="flex flex-col gap-3">
      {SOURCES.map((source) => (
        <div
          key={source.title}
          className="mkt-card flex items-start gap-3 rounded-xl border p-4 shadow-sm"
          style={{ "--mkt-accent": "var(--mkt-violet)" } as React.CSSProperties}
        >
          <MatchRing score={source.match} />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
              <span className="text-sm font-semibold text-[var(--mkt-text)]">{source.title}</span>
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
  );
}

function ResponseScreen() {
  return (
    <div className="mkt-card mkt-card--emphasis rounded-2xl border-2 p-6 shadow-md" style={{ "--mkt-accent": "var(--mkt-violet)" } as React.CSSProperties}>
      <div className="mb-3 flex items-center gap-2">
        <span
          className="flex size-6 items-center justify-center rounded-full"
          style={{ background: "color-mix(in oklch, var(--mkt-violet) 18%, transparent)" }}
        >
          <Bot className="size-3.5" style={{ color: "var(--mkt-violet)" }} />
        </span>
        <span className="text-xs font-medium tracking-[0.06em] text-[var(--mkt-text-muted)] uppercase">
          Generated reply
        </span>
      </div>
      <p className="text-base leading-relaxed text-[var(--mkt-text)]">
        Thanks for flagging this — I can see two charges on the same order. Duplicate charges like
        this are reviewed automatically and reversed to your original payment method once
        confirmed
        <sup className="mx-0.5 font-semibold" style={{ color: "var(--mkt-violet)" }}>
          [1]
        </sup>
        <sup className="mx-0.5 font-semibold" style={{ color: "var(--mkt-violet)" }}>
          [2]
        </sup>
        . Given the billing impact, I&apos;ve marked this high priority.
      </p>
      <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--mkt-text-muted)]/10 pt-4">
        {CITATIONS.map((citation) => (
          <span
            key={citation.mark}
            className="rounded-full border px-2.5 py-1 text-xs font-medium text-[var(--mkt-text-muted)]"
            style={{ borderColor: "color-mix(in oklch, var(--mkt-text-muted) 25%, transparent)" }}
          >
            {citation.mark} {citation.label}
          </span>
        ))}
      </div>
    </div>
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
