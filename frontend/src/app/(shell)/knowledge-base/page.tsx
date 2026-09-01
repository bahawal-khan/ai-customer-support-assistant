import type { Metadata } from "next";

import { KnowledgeView } from "@/features/knowledge-base/knowledge-view";

export const metadata: Metadata = { title: "Knowledge Base" };

export default function KnowledgeBasePage() {
  return <KnowledgeView />;
}
