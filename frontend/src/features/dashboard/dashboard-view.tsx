"use client";

import * as React from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/error-state";
import { getDashboardData, type DashboardData } from "@/lib/api/dashboard";
import { ApiError } from "@/types/api";
import { KpiCards } from "@/features/dashboard/kpi-cards";
import { TrendChart } from "@/features/dashboard/trend-chart";
import { CategoryChart } from "@/features/dashboard/category-chart";
import { RecentComplaints } from "@/features/dashboard/recent-complaints";
import { QuickAnalyzeCta } from "@/features/dashboard/quick-analyze-cta";
import { AssistantPanel } from "@/features/dashboard/assistant-panel";

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Skeleton className="h-72 rounded-xl" />
        <Skeleton className="h-72 rounded-xl" />
      </div>
    </div>
  );
}

export function DashboardView() {
  const [data, setData] = React.useState<DashboardData | null>(null);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [reloadKey, setReloadKey] = React.useState(0);

  React.useEffect(() => {
    let active = true;
    getDashboardData()
      .then((result) => {
        if (!active) return;
        setData(result);
        setLoadError(null);
      })
      .catch((err) => {
        if (!active) return;
        setLoadError(err instanceof ApiError ? err.message : "Couldn't load dashboard data.");
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  if (loadError) return <ErrorState message={loadError} onRetry={() => setReloadKey((k) => k + 1)} />;
  if (!data) return <DashboardSkeleton />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          An overview of complaint volume, sentiment, and support knowledge coverage.
        </p>
      </div>

      <QuickAnalyzeCta />

      <KpiCards kpis={data.kpis} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrendChart data={data.trend} />
        <CategoryChart data={data.categories} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentComplaints recent={data.recent} />
        </div>
        <AssistantPanel data={data} />
      </div>
    </div>
  );
}
