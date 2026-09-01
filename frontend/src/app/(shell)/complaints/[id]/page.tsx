import type { Metadata } from "next";

import { AnalysisView } from "@/features/analysis/analysis-view";

export const metadata: Metadata = { title: "Analysis Results" };

export default async function AnalysisPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AnalysisView complaintId={id} />;
}
