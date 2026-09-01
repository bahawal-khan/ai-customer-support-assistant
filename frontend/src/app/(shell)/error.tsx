"use client";

import { AlertTriangle, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function ShellError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
      <AlertTriangle className="size-8 text-destructive" />
      <div>
        <p className="font-medium">Something went wrong</p>
        <p className="text-sm text-muted-foreground">
          This page hit an unexpected error. You can try again.
        </p>
      </div>
      <Button variant="outline" onClick={reset}>
        <RotateCcw className="size-4" />
        Try again
      </Button>
    </div>
  );
}
