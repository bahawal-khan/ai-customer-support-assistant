"use client";

import Link from "next/link";
import { Bot } from "lucide-react";

import { NavLinks } from "@/components/shell/nav-links";

export function MobileNav() {
  return (
    <div className="flex h-full flex-col bg-sidebar px-3 py-4">
      <Link href="/" className="mb-4 flex items-center gap-2 px-3 font-semibold tracking-tight">
        <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Bot className="size-4" />
        </span>
        AI Customer Support
      </Link>
      <NavLinks layoutId="mobile-active" />
    </div>
  );
}
