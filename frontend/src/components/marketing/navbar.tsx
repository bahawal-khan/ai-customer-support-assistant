import Link from "next/link";
import { Bot } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/shell/theme-toggle";

export function MarketingNavbar() {
  return (
    <header className="mkt sticky top-0 z-40 border-b border-[var(--mkt-text-muted)]/15 bg-[var(--mkt-bg)]/80 text-[var(--mkt-text)] backdrop-blur-md">
      <div className="content-container flex h-14 items-center gap-3">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span
            className="flex size-7 items-center justify-center rounded-lg text-white"
            style={{ background: "var(--mkt-violet)" }}
          >
            <Bot className="size-4" />
          </span>
          <span>AI Customer Support</span>
        </Link>

        <div className="ml-auto flex items-center gap-2">
          <ThemeToggle />
          <Button
            asChild
            size="sm"
            className="shadow-none transition-shadow duration-300 hover:shadow-[0_6px_20px_-6px_var(--mkt-violet)]"
          >
            <Link href="/complaints/new">Use It Free</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
