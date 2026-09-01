import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";
import { PRIORITY_TONE, SENTIMENT_TONE, formatRelativeTime, toTitleCase, truncate } from "@/lib/format";
import type { DashboardData } from "@/lib/api/dashboard";

export function RecentComplaints({ recent }: { recent: DashboardData["recent"] }) {
  return (
    <Card className="shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Complaints</CardTitle>
        <Link
          href="/history"
          className="flex items-center gap-1 text-sm text-primary hover:underline"
        >
          View all <ArrowUpRight className="size-3.5" />
        </Link>
      </CardHeader>
      <CardContent>
        {recent.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No complaints analyzed yet. Try the New Complaint page.
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {recent.map((c) => (
              <li key={c.complaint_id}>
                <Link
                  href={`/complaints/${c.complaint_id}`}
                  className="flex items-center justify-between gap-4 py-3.5 transition-colors hover:bg-muted/50 -mx-(--card-spacing) px-(--card-spacing)"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{truncate(c.text, 70)}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {toTitleCase(c.intent)} &middot; {formatRelativeTime(c.created_at)}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <StatusBadge
                      tone={SENTIMENT_TONE[c.sentiment] ?? "neutral"}
                      label={c.sentiment}
                      className="px-2.5 py-0.5"
                    />
                    <StatusBadge
                      tone={PRIORITY_TONE[c.priority] ?? "neutral"}
                      label={c.priority}
                      className="px-2.5 py-0.5"
                    />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
