import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { ResponseCard } from "@/features/analysis/response-card";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: toastSuccess, error: toastError },
}));

describe("ResponseCard", () => {
  beforeEach(() => {
    toastSuccess.mockClear();
    toastError.mockClear();
  });

  it("renders the generated response text", () => {
    render(<ResponseCard response="We're sorry for the trouble, here's your refund." />);

    expect(
      screen.getByText("We're sorry for the trouble, here's your refund.")
    ).toBeInTheDocument();
  });

  it("renders a fallback message when there is no response", () => {
    render(<ResponseCard response={null} />);

    expect(screen.getByText(/No response was generated/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /copy/i })).toBeDisabled();
  });

  it("copies the response to the clipboard and shows a success toast", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });

    render(<ResponseCard response="Grounded answer text" />);

    fireEvent.click(screen.getByRole("button", { name: /copy/i }));

    await waitFor(() => expect(writeText).toHaveBeenCalledWith("Grounded answer text"));
    await waitFor(() => expect(toastSuccess).toHaveBeenCalledWith("Response copied to clipboard"));
    expect(toastError).not.toHaveBeenCalled();
  });

  it("shows an error toast when the clipboard write fails", async () => {
    const writeText = vi.fn().mockRejectedValue(new Error("denied"));
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });

    render(<ResponseCard response="Grounded answer text" />);

    fireEvent.click(screen.getByRole("button", { name: /copy/i }));

    await waitFor(() => expect(toastError).toHaveBeenCalledWith("Couldn't copy to clipboard"));
    expect(toastSuccess).not.toHaveBeenCalled();
  });
});
