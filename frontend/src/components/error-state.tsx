import { AlertTriangle, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

/** Shared load-failure state; mirrors app/(shell)/error.tsx's visual pattern
 * for failures that happen inside a `useEffect` fetch rather than render
 * (so the route-level error boundary never sees them). */
export function ErrorState({
  message = "Something went wrong while loading this page.",
  onRetry,
}: {
  message?: string;
  onRetry: () => void;
}) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
      <AlertTriangle className="size-8 text-destructive" />
      <div>
        <p className="font-medium">Something went wrong</p>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      <Button variant="outline" onClick={onRetry}>
        <RotateCcw className="size-4" />
        Try again
      </Button>
    </div>
  );
}
