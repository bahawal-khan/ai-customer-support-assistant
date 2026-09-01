"use client";

import { motion } from "motion/react";
import { Gauge, Heart, ShieldAlert, Tags } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";
import { PRIORITY_TONE, SENTIMENT_TONE, formatPercent, toTitleCase } from "@/lib/format";
import type { ComplaintDetailResponse } from "@/types/api";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" as const } },
};

export function HeadlineCards({ analysis }: { analysis: ComplaintDetailResponse }) {
  const overallConfidence = (analysis.intent.confidence + analysis.sentiment.confidence) / 2;

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      <motion.div variants={item}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Intent</CardTitle>
            <Tags className="size-4 text-info" />
          </CardHeader>
          <CardContent>
            <p className="text-lg font-semibold tracking-tight">{toTitleCase(analysis.intent.label)}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {formatPercent(analysis.intent.confidence)} confidence · {analysis.intent.model_version}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Sentiment</CardTitle>
            <Heart className="size-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <StatusBadge
              tone={SENTIMENT_TONE[analysis.sentiment.label] ?? "neutral"}
              label={analysis.sentiment.label}
              className="text-sm"
            />
            <p className="mt-2 text-xs text-muted-foreground">
              {formatPercent(analysis.sentiment.confidence)} confidence
            </p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Priority</CardTitle>
            <ShieldAlert className="size-4 text-warning" />
          </CardHeader>
          <CardContent>
            <StatusBadge tone={PRIORITY_TONE[analysis.priority.level] ?? "neutral"} label={analysis.priority.level} className="text-sm" />
            <p className="mt-2 text-xs text-muted-foreground">{analysis.priority.reason}</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overall Confidence</CardTitle>
            <Gauge className="size-4 text-success" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tabular-nums tracking-tight">
              {formatPercent(overallConfidence)}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">Blended intent + sentiment confidence</p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
