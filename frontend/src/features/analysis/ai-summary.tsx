import { Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent, toTitleCase } from "@/lib/format";
import type { ComplaintDetailResponse } from "@/types/api";

export function AiSummary({ analysis }: { analysis: ComplaintDetailResponse }) {
  const summary = `This complaint was classified as "${toTitleCase(analysis.intent.label)}" with ${formatPercent(
    analysis.intent.confidence
  )} confidence, showing ${analysis.sentiment.label} sentiment. It was assigned ${analysis.priority.level} priority: ${
    analysis.priority.reason
  }`;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4 text-primary" />
          AI Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed text-muted-foreground">{summary}</p>
      </CardContent>
    </Card>
  );
}
