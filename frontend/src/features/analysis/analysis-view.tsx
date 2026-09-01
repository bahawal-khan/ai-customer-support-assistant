"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft, BookOpen, Bot, MessageSquareQuote, SearchX, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/error-state";
import { StepIndicator } from "@/features/complaint/step-indicator";
import { StageHeading } from "@/features/analysis/stage-heading";
import { HeadlineCards } from "@/features/analysis/headline-cards";
import { AiSummary } from "@/features/analysis/ai-summary";
import { SourcesList } from "@/features/analysis/sources-list";
import { ResponseCard } from "@/features/analysis/response-card";
import { getComplaint } from "@/lib/api/client";
import { ApiError, type ComplaintDetailResponse } from "@/types/api";

function AnalysisSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-24 rounded-xl" />
      <Skeleton className="h-48 rounded-xl" />
    </div>
  );
}

function NotFoundState() {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
      <SearchX className="size-8 text-muted-foreground" />
      <div>
        <p className="font-medium">Analysis not found</p>
        <p className="text-sm text-muted-foreground">
          This complaint may not exist, or hasn&apos;t been analyzed in this browser session.
        </p>
      </div>
      <Button asChild variant="outline">
        <Link href="/complaints/new">
          <ArrowLeft className="size-4" />
          Analyze a new complaint
        </Link>
      </Button>
    </div>
  );
}

export function AnalysisView({ complaintId }: { complaintId: string }) {
  const [analysis, setAnalysis] = React.useState<ComplaintDetailResponse | null | undefined>(undefined);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [reloadKey, setReloadKey] = React.useState(0);

  React.useEffect(() => {
    let active = true;
    getComplaint(complaintId)
      .then((result) => {
        if (!active) return;
        setAnalysis(result);
        setLoadError(null);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 404) {
          setAnalysis(null);
          setLoadError(null);
        } else {
          setLoadError(
            err instanceof ApiError ? err.message : "Couldn't load this analysis. Please try again."
          );
        }
      });
    return () => {
      active = false;
    };
  }, [complaintId, reloadKey]);

  if (loadError) return <ErrorState message={loadError} onRetry={() => setReloadKey((k) => k + 1)} />;
  if (analysis === undefined) return <AnalysisSkeleton />;
  if (analysis === null) return <NotFoundState />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analysis Results</h1>
        <p className="text-sm text-muted-foreground">
          The AI pipeline&apos;s complaint, analysis, retrieval, and response stages.
        </p>
      </div>

      <StepIndicator current={2} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="space-y-3">
            <StageHeading step={1} label="Customer Complaint" icon={MessageSquareQuote} />
            <div className="rounded-xl border border-border bg-card p-4">
              <p className="text-sm leading-relaxed text-muted-foreground italic">&ldquo;{analysis.text}&rdquo;</p>
            </div>
          </section>

          <section className="space-y-3">
            <StageHeading step={2} label="AI Analysis" icon={Sparkles} />
            <div className="space-y-4">
              <HeadlineCards analysis={analysis} />
              <AiSummary analysis={analysis} />
            </div>
          </section>

          <section className="space-y-3">
            <StageHeading step={3} label="Knowledge Retrieved" icon={BookOpen} />
            <SourcesList sources={analysis.retrieved_sources} />
          </section>
        </div>

        <section className="space-y-3 lg:sticky lg:top-20 lg:self-start lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto">
          <StageHeading step={4} label="AI Generated Response" icon={Bot} />
          <ResponseCard response={analysis.suggested_response} />
        </section>
      </div>
    </div>
  );
}
