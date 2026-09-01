"use client";

import * as React from "react";
import { ChevronsLeft, ChevronsRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { NavLinks } from "@/components/shell/nav-links";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside
      className={cn(
        "sticky top-14 hidden shrink-0 flex-col border-r border-sidebar-border bg-sidebar px-3 py-4 transition-[width] duration-200 lg:flex",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className={cn(collapsed && "[&_.nav-label]:hidden")}>
        <NavLinks layoutId="sidebar-active" />
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="mt-2 self-end text-sidebar-foreground/60 hover:text-sidebar-foreground"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        onClick={() => setCollapsed((c) => !c)}
      >
        {collapsed ? <ChevronsRight className="size-4" /> : <ChevronsLeft className="size-4" />}
      </Button>
    </aside>
  );
}
