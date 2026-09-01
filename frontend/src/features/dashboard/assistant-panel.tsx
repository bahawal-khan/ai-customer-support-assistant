import { AlertTriangle, BookOpenCheck, Sparkles, TrendingDown, TrendingUp, type LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent, toTitleCase } from "@/lib/format";
import type { DashboardData } from "@/lib/api/dashboard";

type InsightTone = "info" | "warning" | "destructive" | "success";

interface Insight {
  text: string;
  icon: LucideIcon;
  tone: InsightTone;
}

const TONE_CHIP: Record<InsightTone, string> = {
  info: "bg-info/10 text-info dark:bg-info/15",
  warning: "bg-warning/15 text-warning-foreground dark:bg-warning/20 dark:text-warning",
  destructive: "bg-destructive/10 text-destructive dark:bg-destructive/20",
  success: "bg-success/10 text-success dark:bg-success/15",
};

function buildInsights(data: DashboardData): Insight[] {
  const insights: Insight[] = [];
  const topCategory = data.categories[0];

  if (topCategory) {
    insights.push({
      text: `${toTitleCase(topCategory.intent)} is the most common complaint category, with ${topCategory.count} case${
        topCategory.count === 1 ? "" : "s"
      } analyzed.`,
      icon: TrendingUp,
      tone: "info",
    });
  }
  if (data.kpis.highPriorityOpen > 0) {
    insights.push({
      text: `${data.kpis.highPriorityOpen} complaint${data.kpis.highPriorityOpen === 1 ? "" : "s"} are flagged high or critical priority and may need attention.`,
      icon: AlertTriangle,
      tone: "warning",
    });
  }
  if (data.kpis.negativeSentimentShare > 0) {
    insights.push({
      text: `${formatPercent(data.kpis.negativeSentimentShare)} of recent complaints carry negative sentiment.`,
      icon: TrendingDown,
      tone: "destructive",
    });
  }
  insights.push({
    text: `Knowledge base coverage: ${data.documentsIndexed} of ${data.documentsTotal} documents indexed.`,
    icon: BookOpenCheck,
    tone: "success",
  });

  return insights;
}

export function AssistantPanel({ data }: { data: DashboardData }) {
  const insights = buildInsights(data);

  return (
    <Card className="border-primary/10 bg-gradient-to-br from-accent/50 to-accent/15 shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4 text-primary" />
          AI Assistant
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {insights.map((insight, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm">
              <span
                className={`flex size-6 shrink-0 items-center justify-center rounded-full ${TONE_CHIP[insight.tone]}`}
              >
                <insight.icon className="size-3.5" />
              </span>
              <span className="pt-0.5 text-muted-foreground">{insight.text}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
