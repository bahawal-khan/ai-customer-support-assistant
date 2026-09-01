import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { NewComplaintView } from "@/features/complaint/new-complaint-view";
import { ApiError } from "@/types/api";

const { push, analyzeComplaint } = vi.hoisted(() => ({
  push: vi.fn(),
  analyzeComplaint: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/api/client", () => ({
  analyzeComplaint,
}));

function fillComplaintText(text: string) {
  fireEvent.change(screen.getByLabelText("Complaint description"), {
    target: { value: text },
  });
}

describe("NewComplaintView", () => {
  afterEach(() => {
    push.mockReset();
    analyzeComplaint.mockReset();
  });

  it("disables submit until valid complaint text is entered", () => {
    render(<NewComplaintView />);

    const button = screen.getByRole("button", { name: /analyze complaint/i });
    expect(button).toBeDisabled();

    fillComplaintText("My order never arrived.");
    expect(button).toBeEnabled();
  });

  it("shows the analyzing/loading pipeline after submit", async () => {
    analyzeComplaint.mockReturnValue(new Promise(() => {})); // never resolves
    render(<NewComplaintView />);

    fillComplaintText("My order never arrived.");
    fireEvent.click(screen.getByRole("button", { name: /analyze complaint/i }));

    expect(await screen.findByText(/analyzing your complaint/i)).toBeInTheDocument();
    expect(screen.getByText(/analyzing complaint/i)).toBeInTheDocument();
  });

  it("navigates to the analysis page once the backend responds", async () => {
    analyzeComplaint.mockResolvedValue({
      request_id: "req-1",
      complaint_id: "complaint-123",
      intent: { label: "get_refund", confidence: 0.9, model_version: "v1" },
      sentiment: { label: "negative", confidence: 0.8 },
      priority: { level: "high", reason: "sensitive intent" },
      retrieved_sources: [],
      suggested_response: "We're sorry to hear that.",
      model_metadata: {
        intent_model_version: "v1",
        embedding_model: "minilm",
        llm_provider: "groq",
        llm_model: "gpt-oss",
        prompt_version: "v1",
        retrieved_source_count: 0,
        llm_available: true,
      },
    });
    render(<NewComplaintView />);

    fillComplaintText("My order never arrived.");
    fireEvent.click(screen.getByRole("button", { name: /analyze complaint/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/complaints/complaint-123"), {
      timeout: 5000,
    });
  });

  it("shows an error banner and returns to the form when analysis fails", async () => {
    analyzeComplaint.mockRejectedValue(
      new ApiError(503, {
        error: { code: "model_unavailable", message: "The intent model is unavailable.", request_id: "r1" },
      })
    );
    render(<NewComplaintView />);

    fillComplaintText("My order never arrived.");
    fireEvent.click(screen.getByRole("button", { name: /analyze complaint/i }));

    expect(await screen.findByText("The intent model is unavailable.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /analyze complaint/i })).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });

  it("shows a generic error message for non-API failures", async () => {
    analyzeComplaint.mockRejectedValue(new Error("network down"));
    render(<NewComplaintView />);

    fillComplaintText("My order never arrived.");
    fireEvent.click(screen.getByRole("button", { name: /analyze complaint/i }));

    expect(
      await screen.findByText(/something went wrong while analyzing this complaint/i)
    ).toBeInTheDocument();
  });
});
