import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HistoryView } from "@/features/history/history-view";
import { ApiError } from "@/types/api";

const { push, listComplaints, deleteComplaints, toastSuccess, toastError } = vi.hoisted(() => ({
  push: vi.fn(),
  listComplaints: vi.fn(),
  deleteComplaints: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/api/client", () => ({
  listComplaints,
  deleteComplaints,
}));

vi.mock("sonner", () => ({
  toast: { success: toastSuccess, error: toastError },
}));

function page(items: ReturnType<typeof makeItem>[]) {
  return {
    items,
    page: 1,
    page_size: 8,
    total: items.length,
    total_pages: 1,
  };
}

function makeItem(id: string, text: string) {
  return {
    complaint_id: id,
    text,
    intent: "get_refund",
    intent_confidence: 0.9,
    sentiment: "negative",
    sentiment_confidence: 0.8,
    priority: "high",
    created_at: "2026-08-01T00:00:00Z",
  };
}

describe("HistoryView delete flow", () => {
  afterEach(() => {
    push.mockReset();
    listComplaints.mockReset();
    deleteComplaints.mockReset();
    toastSuccess.mockReset();
    toastError.mockReset();
  });

  it("shows no selection toolbar until a row is checked", async () => {
    listComplaints.mockResolvedValue(page([makeItem("c1", "Where is my refund?")]));
    render(<HistoryView />);

    expect(await screen.findByText("Where is my refund?")).toBeInTheDocument();
    expect(screen.queryByText(/selected/i)).not.toBeInTheDocument();
  });

  it("selects a row, confirms delete, and refreshes the list on success", async () => {
    listComplaints
      .mockResolvedValueOnce(page([makeItem("c1", "Where is my refund?")]))
      .mockResolvedValueOnce(page([]));
    deleteComplaints.mockResolvedValue({ deleted_ids: ["c1"] });

    render(<HistoryView />);
    await screen.findByText("Where is my refund?");

    fireEvent.click(screen.getByRole("checkbox", { name: /select complaint/i }));
    expect(await screen.findByText("1 complaint selected")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^delete$/i }));
    const dialog = await screen.findByRole("alertdialog");
    fireEvent.click(within(dialog).getByRole("button", { name: /^delete$/i }));

    await waitFor(() => expect(deleteComplaints).toHaveBeenCalledWith(["c1"]));
    await waitFor(() => expect(toastSuccess).toHaveBeenCalledWith("1 complaint deleted"));
    await waitFor(() => expect(listComplaints).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(screen.queryByText("Where is my refund?")).not.toBeInTheDocument()
    );
    expect(screen.queryByText(/selected/i)).not.toBeInTheDocument();
    expect(toastError).not.toHaveBeenCalled();
  });

  it("keeps rows and shows an error toast when delete fails", async () => {
    listComplaints.mockResolvedValue(page([makeItem("c1", "Where is my refund?")]));
    deleteComplaints.mockRejectedValue(
      new ApiError(404, { error: { code: "not_found", message: "Complaint not found.", request_id: "r1" } })
    );

    render(<HistoryView />);
    await screen.findByText("Where is my refund?");

    fireEvent.click(screen.getByRole("checkbox", { name: /select complaint/i }));
    fireEvent.click(screen.getByRole("button", { name: /^delete$/i }));
    const dialog = await screen.findByRole("alertdialog");
    fireEvent.click(within(dialog).getByRole("button", { name: /^delete$/i }));

    await waitFor(() => expect(toastError).toHaveBeenCalledWith("Complaint not found."));
    expect(listComplaints).toHaveBeenCalledTimes(1);
    expect(screen.getByText("Where is my refund?")).toBeInTheDocument();
  });

  it("select-all checkbox selects every row on the page", async () => {
    listComplaints.mockResolvedValue(
      page([makeItem("c1", "First complaint"), makeItem("c2", "Second complaint")])
    );
    render(<HistoryView />);
    await screen.findByText("First complaint");

    fireEvent.click(screen.getByRole("checkbox", { name: /select all complaints/i }));

    expect(await screen.findByText("2 complaints selected")).toBeInTheDocument();
  });
});
