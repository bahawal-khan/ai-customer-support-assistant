"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PipelinePreview } from "@/components/marketing/pipeline-preview";
import { useMktMotion } from "@/components/marketing/mkt-motion";

export function Hero() {
  const { item } = useMktMotion();

  return (
    <section
      id="hero"
      className="mkt relative scroll-mt-14 overflow-hidden bg-[var(--mkt-bg)] text-[var(--mkt-text)]"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 -left-24 size-72 rounded-full opacity-20 blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-violet)" }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 -bottom-24 size-80 rounded-full opacity-20 blur-3xl motion-reduce:hidden"
        style={{ background: "var(--mkt-amber)" }}
      />

      <div className="content-container relative flex flex-col items-center gap-16 py-20 text-center sm:py-28">
        <motion.div
          initial="hidden"
          animate="show"
          variants={item}
          className="flex flex-col items-center gap-5"
        >
          <div className="flex items-center gap-2 text-xs font-medium tracking-[0.14em] text-[var(--mkt-text-muted)] uppercase">
            <span className="size-1.5 rounded-full" style={{ background: "var(--mkt-violet)" }} />
            AI Customer Support
          </div>

          <h1 className="font-display max-w-3xl text-[clamp(2.75rem,6vw,4.5rem)] leading-[1.05] tracking-[-0.02em] text-balance">
            Turn every complaint into a structured, grounded response
          </h1>

          <p className="max-w-xl text-lg leading-relaxed text-[var(--mkt-text-muted)] sm:text-xl">
            Submit a customer complaint and get intent, sentiment, and priority classification,
            relevant knowledge base sources, and an AI-generated response grounded in your own
            documentation — never invented.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Button
              asChild
              size="lg"
              className="shadow-none transition-shadow duration-300 hover:shadow-[0_10px_32px_-10px_var(--mkt-violet)]"
            >
              <Link href="/complaints/new">
                Use It Free <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="!bg-transparent text-[var(--mkt-text)] shadow-none transition-shadow duration-300 hover:!bg-[var(--mkt-surface)] hover:shadow-[0_10px_32px_-12px_var(--mkt-amber)]"
            >
              <Link href="/dashboard">View Dashboard</Link>
            </Button>
          </div>
        </motion.div>

        <div className="w-full max-w-4xl">
          <PipelinePreview />
        </div>
      </div>
    </section>
  );
}
