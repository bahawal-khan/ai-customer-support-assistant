"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toTitleCase } from "@/lib/format";
import type { CategoryPoint } from "@/lib/api/dashboard";

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function colorForIntent(intent: string): string {
  let hash = 0;
  for (let i = 0; i < intent.length; i++) {
    hash = (hash * 31 + intent.charCodeAt(i)) >>> 0;
  }
  return CHART_COLORS[hash % CHART_COLORS.length];
}

export function CategoryChart({ data }: { data: CategoryPoint[] }) {
  const total = data.reduce((sum, d) => sum + d.count, 0);
  const segments = data.map((d) => ({
    ...d,
    label: toTitleCase(d.intent),
    color: colorForIntent(d.intent),
    percent: total > 0 ? d.count / total : 0,
  }));

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>Category Distribution</CardTitle>
      </CardHeader>
      <CardContent className="pt-2">
        {segments.length === 0 ? (
          <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
            No complaints analyzed yet.
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex h-3.5 w-full overflow-hidden rounded-full bg-muted">
              {segments.map((s) => (
                <div
                  key={s.intent}
                  title={`${s.label}: ${s.count} (${Math.round(s.percent * 100)}%)`}
                  className="h-full transition-opacity hover:opacity-80"
                  style={{ width: `${s.percent * 100}%`, backgroundColor: s.color }}
                />
              ))}
            </div>
            <ul className="space-y-3">
              {segments.map((s) => (
                <li key={s.intent} className="flex items-center gap-3 text-sm">
                  <span
                    className="size-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: s.color }}
                  />
                  <span className="min-w-0 flex-1 truncate">{s.label}</span>
                  <span className="shrink-0 tabular-nums text-muted-foreground">
                    {s.count} &middot; {Math.round(s.percent * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
