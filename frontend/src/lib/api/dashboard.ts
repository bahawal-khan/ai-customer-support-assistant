import { listComplaints, listDocuments } from "@/lib/api/client";

export interface DashboardKpis {
  totalComplaints: number;
  highPriorityOpen: number;
  avgIntentConfidence: number;
  negativeSentimentShare: number;
}

export interface TrendPoint {
  date: string;
  count: number;
}

export interface CategoryPoint {
  intent: string;
  count: number;
}

export interface DashboardData {
  kpis: DashboardKpis;
  trend: TrendPoint[];
  categories: CategoryPoint[];
  recent: Array<{
    complaint_id: string;
    text: string;
    intent: string;
    priority: string;
    sentiment: string;
    created_at: string;
  }>;
  documentsIndexed: number;
  documentsTotal: number;
}

/**
 * There is no dedicated dashboard/aggregation endpoint (docs/api/API_SPEC.md
 * only defines GET /complaints, paginated, page_size capped at 100). KPIs,
 * the trend chart, and the category chart are computed client-side over the
 * most recent page of complaints, same as Task 13's mock aggregation, but
 * `totalComplaints` uses the API's true `total` count rather than the
 * sample size. For a history larger than 100 complaints, the other KPIs and
 * charts are computed over the most recent 100 rather than the full table.
 */
const DASHBOARD_SAMPLE_SIZE = 100;

export async function getDashboardData(): Promise<DashboardData> {
  const [complaintsPage, documents] = await Promise.all([
    listComplaints({ page: 1, page_size: DASHBOARD_SAMPLE_SIZE }),
    listDocuments(),
  ]);
  const complaints = complaintsPage.items;
  const sampled = complaints.length;

  const highPriorityOpen = complaints.filter(
    (c) => c.priority === "high" || c.priority === "critical"
  ).length;
  const avgIntentConfidence =
    sampled > 0 ? complaints.reduce((sum, c) => sum + c.intent_confidence, 0) / sampled : 0;
  const negativeSentimentShare =
    sampled > 0 ? complaints.filter((c) => c.sentiment === "negative").length / sampled : 0;

  const trendMap = new Map<string, number>();
  const days = 14;
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
    trendMap.set(date.toISOString().slice(0, 10), 0);
  }
  for (const complaint of complaints) {
    const key = complaint.created_at.slice(0, 10);
    if (trendMap.has(key)) {
      trendMap.set(key, (trendMap.get(key) ?? 0) + 1);
    }
  }
  const trend: TrendPoint[] = Array.from(trendMap.entries()).map(([date, count]) => ({ date, count }));

  const categoryMap = new Map<string, number>();
  for (const complaint of complaints) {
    categoryMap.set(complaint.intent, (categoryMap.get(complaint.intent) ?? 0) + 1);
  }
  const categories: CategoryPoint[] = Array.from(categoryMap.entries())
    .map(([intent, count]) => ({ intent, count }))
    .sort((a, b) => b.count - a.count);

  const recent = complaints.slice(0, 6).map((c) => ({
    complaint_id: c.complaint_id,
    text: c.text,
    intent: c.intent,
    priority: c.priority,
    sentiment: c.sentiment,
    created_at: c.created_at,
  }));

  return {
    kpis: {
      totalComplaints: complaintsPage.total,
      highPriorityOpen,
      avgIntentConfidence,
      negativeSentimentShare,
    },
    trend,
    categories,
    recent,
    documentsIndexed: documents.items.filter((d) => d.status === "indexed").length,
    documentsTotal: documents.total,
  };
}
