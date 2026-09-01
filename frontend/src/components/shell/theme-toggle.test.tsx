import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { TooltipProvider } from "@/components/ui/tooltip";

function renderWithTheme() {
  return render(
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
      <TooltipProvider>
        <ThemeToggle />
      </TooltipProvider>
    </ThemeProvider>
  );
}

describe("ThemeToggle", () => {
  it("starts in light mode and shows a moon icon to switch to dark", async () => {
    renderWithTheme();

    const button = await screen.findByRole("button", { name: /toggle theme/i });
    await waitFor(() => expect(document.documentElement.classList.contains("light")).toBe(true));
    expect(button.querySelector(".lucide-moon")).toBeInTheDocument();
  });

  it("switches to dark mode when clicked, and back to light on a second click", async () => {
    renderWithTheme();

    const button = await screen.findByRole("button", { name: /toggle theme/i });
    await waitFor(() => expect(document.documentElement.classList.contains("light")).toBe(true));

    fireEvent.click(button);
    await waitFor(() => expect(document.documentElement.classList.contains("dark")).toBe(true));
    expect(button.querySelector(".lucide-sun")).toBeInTheDocument();

    fireEvent.click(button);
    await waitFor(() => expect(document.documentElement.classList.contains("light")).toBe(true));
    expect(button.querySelector(".lucide-moon")).toBeInTheDocument();
  });
});
