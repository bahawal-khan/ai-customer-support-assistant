"use client";

import * as React from "react";
import { motion } from "motion/react";
import { ChevronDown } from "lucide-react";

import { useMktMotion } from "@/components/marketing/mkt-motion";

const FAQS = [
  {
    question: "How does the AI decide what a complaint is about?",
    answer:
      "A DistilBERT classifier reads the complaint text and predicts an intent label and sentiment, each with its own confidence score. Both run independently of the response-generation step.",
  },
  {
    question: "Does the AI make things up, or only use our own documentation?",
    answer:
      "The generation step is instructed to treat the retrieved knowledge base passages as the only source for policy or factual claims, and to never use outside knowledge for those claims.",
  },
  {
    question: "What happens if the knowledge base doesn't have a matching answer?",
    answer:
      "If retrieval finds no sufficiently relevant passages, the model is told explicitly that the knowledge base doesn't have enough information and is instructed to say so and recommend escalation, rather than guessing.",
  },
  {
    question: "Can we add our own documents to the knowledge base?",
    answer:
      "Yes. Documents can be uploaded, indexed into chunks and embeddings, and removed again through the knowledge base API — retrieval runs against whatever is currently indexed.",
  },
  {
    question: "How is priority decided?",
    answer:
      "By a fixed rule, not a model: negative sentiment on a sensitive intent (billing, refunds, cancellations, account access, escalation requests) is high priority; either one alone is medium; neither is low.",
  },
  {
    question: "How accurate is the classification?",
    answer:
      "There's no single aggregate accuracy number to quote — instead, every intent and sentiment prediction carries its own confidence score, shown alongside the label rather than implied by an overall stat.",
  },
  {
    question: "Does this replace our support agents?",
    answer:
      "No. It classifies each complaint, retrieves relevant sources, and drafts a suggested response for a person to review — it doesn't send replies or close tickets on its own.",
  },
];

export function Faq() {
  const { item } = useMktMotion();
  const [openIndex, setOpenIndex] = React.useState<number | null>(0);

  return (
    <section
      id="faq"
      className="mkt relative scroll-mt-14 overflow-hidden border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] py-20 text-[var(--mkt-text)] sm:py-28"
    >
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
            FAQs
          </div>
          <h2 className="font-display text-[clamp(2rem,4vw,3rem)] leading-[1.1] tracking-[-0.02em] text-balance">
            Questions worth asking before you rely on it
          </h2>
          <p className="max-w-lg text-base leading-relaxed text-[var(--mkt-text-muted)] sm:text-lg">
            Straight answers about what the pipeline actually does, and what it doesn&apos;t.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.2 }}
          variants={item}
          className="mx-auto flex w-full max-w-2xl flex-col gap-3"
        >
          {FAQS.map((faq, index) => {
            const open = index === openIndex;
            return (
              <div
                key={faq.question}
                className="mkt-card overflow-hidden rounded-2xl border shadow-sm"
                style={{ "--mkt-accent": "var(--mkt-violet)" } as React.CSSProperties}
              >
                <button
                  type="button"
                  aria-expanded={open}
                  onClick={() => setOpenIndex(open ? null : index)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors duration-200 sm:px-6"
                >
                  <span className="text-sm font-semibold text-[var(--mkt-text)] sm:text-base">
                    {faq.question}
                  </span>
                  <ChevronDown
                    aria-hidden
                    className="size-4 shrink-0 text-[var(--mkt-text-muted)] transition-transform duration-200 motion-reduce:transition-none"
                    style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
                  />
                </button>
                <div
                  className="grid transition-[grid-template-rows] duration-200 ease-out motion-reduce:transition-none"
                  style={{ gridTemplateRows: open ? "1fr" : "0fr" }}
                >
                  <div className="overflow-hidden">
                    <p className="px-5 pb-4 text-sm leading-relaxed text-[var(--mkt-text-muted)] sm:px-6">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
