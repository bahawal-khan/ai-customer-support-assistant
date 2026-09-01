import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnalysisView } from "@/features/analysis/analysis-view";
import { ApiError } from "@/types/api";

const { getComplaint } = vi.hoisted(() => ({ getComplaint: vi.fn() }));

vi.mock("@/lib/api/client", () => ({ getComplaint }));

const ANALYSIS = {
  complaint_id: "complaint-123",
  text: "My order arrived damaged.",
  created_at: "2026-08-01T00:00:00Z",
  intent: { label: "damaged_item", confidence: 0.92, model_version: "distilbert-v2" },
  sentiment: { label: "negative", confidence: 0.81 },
  priority: { level: "high", reason: "sensitive intent with negative sentiment" },
  retrieved_sources: [
    {
      chunk_id: "chunk-1",
      document_id: "doc-1",
      source_id: "returns-policy",
      title: "Returns Policy",
      category: "returns",
      version: "1.0",
      chunk_index: 0,
      content: "Damaged items can be returned within 30 days.",
      score: 0.87,
      rank: 1,
    },
  ],
  suggested_response: "We're sorry your order arrived damaged, here's how to get a replacement.",
  model_metadata: {
    intent_model_version: "distilbert-v2",
    embedding_model: "minilm",
    llm_provider: "groq",
    llm_model: "gpt-oss",
    prompt_version: "v1",
    retrieved_source_count: 1,
    llm_available: true,
  },
};

describe("AnalysisView", () => {
  afterEach(() => {
    getComplaint.mockReset();
  });

  it("shows a loading skeleton while the analysis is being fetched", () => {
    getComplaint.mockReturnValue(new Promise(() => {}));
    const { container } = render(<AnalysisView complaintId="complaint-123" />);

    expect(container.querySelectorAll('[class*="animate-pulse"]').length).toBeGreaterThan(0);
  });

  it("renders the full analysis result once loaded", async () => {
    getComplaint.mockResolvedValue(ANALYSIS);
    render(<AnalysisView complaintId="complaint-123" />);

    expect(await screen.findByText("Damaged Item")).toBeInTheDocument();
    expect(screen.getAllByText(/negative/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Returns Policy")).toBeInTheDocument();
    expect(
      screen.getByText("We're sorry your order arrived damaged, here's how to get a replacement.")
    ).toBeInTheDocument();
  });

  it("shows a not-found state for a 404", async () => {
    getComplaint.mockRejectedValue(
      new ApiError(404, { error: { code: "not_found", message: "not found", request_id: "r1" } })
    );
    render(<AnalysisView complaintId="unknown" />);

    expect(await screen.findByText(/analysis not found/i)).toBeInTheDocument();
  });

  it("shows an error state with retry for other failures", async () => {
    getComplaint.mockRejectedValue(new Error("network down"));
    render(<AnalysisView complaintId="complaint-123" />);

    expect(await screen.findByText(/couldn't load this analysis/i)).toBeInTheDocument();

    getComplaint.mockResolvedValue(ANALYSIS);
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));

    await waitFor(() => expect(screen.getByText("Damaged Item")).toBeInTheDocument());
  });
});
