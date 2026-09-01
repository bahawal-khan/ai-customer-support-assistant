"use client";

import { motion } from "motion/react";
import { FileText } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { toTitleCase } from "@/lib/format";
import type { RetrievedSource } from "@/types/api";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.15 } },
};

const item = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.22, ease: "easeOut" as const } },
};

function MatchBadge({ score }: { score: number }) {
  const clamped = Math.min(Math.max(score, 0), 1);
  const pct = Math.round(clamped * 100);
  const tint = 12 + clamped * 45;

  return (
    <span
      className="inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-xs font-bold tabular-nums"
      style={{
        backgroundColor: `color-mix(in oklch, var(--success) ${tint}%, transparent)`,
        color: "var(--success)",
      }}
    >
      {pct}% match
    </span>
  );
}

export function SourcesList({ sources }: { sources: RetrievedSource[] }) {
  return (
    <Card>
      <CardContent>
        {sources.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No matching knowledge base sources were found for this complaint.
          </p>
        ) : (
          <motion.ul variants={container} initial="hidden" animate="show" className="space-y-3">
            {sources.map((source) => (
              <motion.li
                key={source.chunk_id ?? `${source.source_id}-${source.chunk_index}`}
                variants={item}
                className="rounded-lg border border-border p-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium">{source.title || source.source_id}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {toTitleCase(source.category)} · v{source.version} · chunk {source.chunk_index}
                    </p>
                  </div>
                  <MatchBadge score={source.score} />
                </div>
                <blockquote className="mt-2 border-l-2 border-border pl-3 text-sm text-muted-foreground">
                  {source.content}
                </blockquote>
                <span className="mt-2 inline-flex w-fit items-center gap-1.5 rounded-md bg-muted/70 px-2 py-1 font-mono text-[11px] text-muted-foreground">
                  <FileText className="size-3 shrink-0" />
                  {source.source_id}
                  <span className="text-muted-foreground/60">· rank {source.rank}</span>
                </span>
              </motion.li>
            ))}
          </motion.ul>
        )}
      </CardContent>
    </Card>
  );
}
