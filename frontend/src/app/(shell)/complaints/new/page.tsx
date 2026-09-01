import type { Metadata } from "next";

import { NewComplaintView } from "@/features/complaint/new-complaint-view";

export const metadata: Metadata = { title: "New Complaint" };

export default function NewComplaintPage() {
  return <NewComplaintView />;
}
