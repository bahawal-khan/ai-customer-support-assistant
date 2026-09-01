"use client";

import { motion } from "motion/react";
import { AlertTriangle, MessageSquare, ShieldCheck, TrendingDown } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent } from "@/lib/format";
import type { DashboardKpis } from "@/lib/api/dashboard";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.22, ease: "easeOut" as const } },
};

export function KpiCards({ kpis }: { kpis: DashboardKpis }) {
  const cards = [
    {
      label: "Total Complaints",
      value: kpis.totalComplaints.toLocaleString(),
      icon: MessageSquare,
      tone: "info",
      caption: "All complaints logged",
    },
    {
      label: "High Priority Open",
      value: kpis.highPriorityOpen.toLocaleString(),
      icon: AlertTriangle,
      tone: "warning",
      caption: "Needs attention",
    },
    {
      label: "Avg. Intent Confidence",
      value: formatPercent(kpis.avgIntentConfidence),
      icon: ShieldCheck,
      tone: "success",
      caption: "Model certainty",
    },
    {
      label: "Negative Sentiment Share",
      value: formatPercent(kpis.negativeSentimentShare),
      icon: TrendingDown,
      tone: "destructive",
      caption: "Of recent complaints",
    },
  ] as const;

  const TONE_CHIP: Record<(typeof cards)[number]["tone"], string> = {
    info: "bg-info/10 text-info dark:bg-info/15",
    warning: "bg-warning/15 text-warning-foreground dark:bg-warning/20 dark:text-warning",
    success: "bg-success/10 text-success dark:bg-success/15",
    destructive: "bg-destructive/10 text-destructive dark:bg-destructive/20",
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      {cards.map((card) => (
        <motion.div key={card.label} variants={item}>
          <Card className="shadow-sm transition-transform hover:-translate-y-0.5">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{card.label}</CardTitle>
              <span className={`flex size-8 shrink-0 items-center justify-center rounded-lg ${TONE_CHIP[card.tone]}`}>
                <card.icon className="size-4" />
              </span>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-semibold tabular-nums tracking-tight">{card.value}</p>
              <p className="mt-1 text-xs text-muted-foreground">{card.caption}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
