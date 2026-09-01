"use client";

import * as React from "react";
import { motion } from "motion/react";
import type { Variants } from "motion/react";
import { Bot, BookOpen, History, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useMktMotion, mktAccentFor } from "@/components/marketing/mkt-motion";

const ANALYSIS_ATTRIBUTES = [
  { label: "Intent", value: "Payment issue" },
  { label: "Sentiment", value: "Negative" },
  { label: "Priority", value: "High" },
];

const RELEVANT_SOURCES = [
  { title: "Payment FAQ", category: "Payment" },
  { title: "Refund Policy", category: "Refund" },
  { title: "Escalation Policy", category: "Escalation" },
];

const HISTORY_ROWS = [
  {
    text: "I was charged twice for the same order and need this fixed.",
    intent: "Payment issue",
    sentiment: "Negative",
    priority: "High",
  },
  {
    text: "My package says delivered but I never received it.",
    intent: "Delivery issue",
  },
  {
    text: "My router keeps dropping the Wi-Fi connection every hour.",
    intent: "Technical support",
  },
];

function badgeStyle(accent: string): React.CSSProperties {
  return {
    color: "var(--mkt-text)",
    borderColor: `color-mix(in oklch, ${accent} 35%, transparent)`,
    background: `color-mix(in oklch, ${accent} 10%, transparent)`,
  };
}

export function Features() {
  const { item, container } = useMktMotion();

  return (
    <section
      id="features"
      className="mkt relative scroll-mt-14 overflow-hidden border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] py-20 text-[var(--mkt-text)] sm:py-28"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 right-0 size-96 -translate-y-1/3 rounded-full opacity-[0.1] blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-amber)" }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute bottom-0 left-1/4 size-80 translate-y-1/3 rounded-full opacity-[0.1] blur-3xl motion-reduce:hidden"
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
            Features &amp; capabilities
          </div>
          <h2 className="font-display text-[clamp(2rem,4vw,3rem)] leading-[1.1] tracking-[-0.02em] text-balance">
            Everything the pipeline gives you
          </h2>
          <p className="max-w-lg text-base leading-relaxed text-[var(--mkt-text-muted)] sm:text-lg">
            Four capabilities working together on every complaint, from first read to a grounded
            reply.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.2 }}
          variants={container}
          className="grid grid-cols-1 gap-6 sm:grid-cols-2"
        >
          <FeatureCard
            index={0}
            icon={Sparkles}
            title="AI Analysis"
            description="Every complaint is classified for intent, sentiment, and priority the moment it's submitted."
            item={item}
          >
            {(accent) => (
              <dl className="flex flex-col divide-y divide-[var(--mkt-text-muted)]/10">
                {ANALYSIS_ATTRIBUTES.map((attr) => (
                  <div
                    key={attr.label}
                    className="flex items-center justify-between gap-4 py-2.5 first:pt-0 last:pb-0"
                  >
                    <dt className="text-sm text-[var(--mkt-text-muted)]">{attr.label}</dt>
                    <dd
                      className="rounded-full border px-2.5 py-1 text-xs font-semibold"
                      style={badgeStyle(accent)}
                    >
                      {attr.value}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </FeatureCard>

          <FeatureCard
            index={1}
            icon={BookOpen}
            title="Knowledge Base + RAG"
            description="pgvector and LangChain retrieve the passages most relevant to each complaint from your own documentation."
            item={item}
          >
            {(accent) => (
              <div>
                <p className="mb-3 text-xs font-medium tracking-[0.08em] text-[var(--mkt-text-muted)] uppercase">
                  3 relevant sources found
                </p>
                <div className="flex flex-col gap-2">
                  {RELEVANT_SOURCES.map((source) => (
                    <div
                      key={source.title}
                      className="mkt-card flex items-center justify-between gap-3 rounded-xl border px-3 py-2"
                      style={{ "--mkt-accent": accent } as React.CSSProperties}
                    >
                      <span className="truncate text-sm font-semibold text-[var(--mkt-text)]">
                        {source.title}
                      </span>
                      <span className="shrink-0 text-[11px] font-medium tracking-[0.06em] text-[var(--mkt-text-muted)] uppercase">
                        {source.category}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </FeatureCard>

          <FeatureCard
            index={2}
            icon={Bot}
            title="AI Response"
            description="Groq drafts a reply that cites the retrieved sources directly — nothing invented."
            item={item}
          >
            {(accent) => (
              <div>
                <div className="mb-2 flex items-center gap-2">
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
                <p className="text-sm leading-relaxed text-[var(--mkt-text)]">
                  Duplicate charges like this are reviewed automatically and reversed to your
                  original payment method once confirmed
                  <sup className="mx-0.5 font-semibold" style={{ color: accent }}>
                    [1]
                  </sup>
                  <sup className="mx-0.5 font-semibold" style={{ color: accent }}>
                    [2]
                  </sup>
                  .
                </p>
                <div className="mt-3 flex flex-wrap gap-2 border-t border-[var(--mkt-text-muted)]/10 pt-3">
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
          </FeatureCard>

          <FeatureCard
            index={3}
            icon={History}
            title="Complaint History"
            description="Every classified complaint is saved and searchable, filterable by intent, sentiment, and priority."
            item={item}
          >
            {(accent) => (
              <div className="flex flex-col divide-y divide-[var(--mkt-text-muted)]/10">
                {HISTORY_ROWS.map((row) => (
                  <div key={row.text} className="flex flex-col gap-2 py-2.5 first:pt-0 last:pb-0">
                    <p className="truncate text-sm text-[var(--mkt-text)]">{row.text}</p>
                    <div className="flex flex-wrap gap-1.5">
                      <span
                        className="rounded-full border px-2 py-0.5 text-[11px] font-medium"
                        style={badgeStyle(accent)}
                      >
                        {row.intent}
                      </span>
                      {row.sentiment && (
                        <span
                          className="rounded-full border px-2 py-0.5 text-[11px] font-medium"
                          style={badgeStyle(accent)}
                        >
                          {row.sentiment}
                        </span>
                      )}
                      {row.priority && (
                        <span
                          className="rounded-full border px-2 py-0.5 text-[11px] font-medium"
                          style={badgeStyle(accent)}
                        >
                          {row.priority}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </FeatureCard>
        </motion.div>
      </div>
    </section>
  );
}

function FeatureCard({
  index,
  icon: Icon,
  title,
  description,
  children,
  item,
}: {
  index: number;
  icon: LucideIcon;
  title: string;
  description: string;
  children: (accent: string) => React.ReactNode;
  item: Variants;
}) {
  const accent = mktAccentFor(index);

  return (
    <motion.div
      variants={item}
      className="mkt-card flex flex-col gap-5 rounded-2xl border p-6 shadow-sm sm:p-7"
      style={{ "--mkt-accent": accent } as React.CSSProperties}
    >
      <div className="flex items-center gap-3">
        <span
          className="flex size-9 shrink-0 items-center justify-center rounded-full"
          style={{ background: `color-mix(in oklch, ${accent} 16%, transparent)` }}
        >
          <Icon className="size-4.5" style={{ color: accent }} />
        </span>
        <div>
          <h3 className="font-heading text-lg font-semibold text-[var(--mkt-text)]">{title}</h3>
        </div>
      </div>
      <p className="-mt-2 text-sm leading-relaxed text-[var(--mkt-text-muted)]">{description}</p>
      <div className="mt-auto">{children(accent)}</div>
    </motion.div>
  );
}
