import Link from "next/link";
import { ArrowRight, MessageSquarePlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function QuickAnalyzeCta() {
  return (
    <Card className="overflow-hidden border-primary/20 bg-gradient-to-br from-primary/5 via-card to-card">
      <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <MessageSquarePlus className="size-5" />
          </span>
          <div>
            <p className="font-medium">Analyze a new complaint</p>
            <p className="text-sm text-muted-foreground">
              Get intent, sentiment, priority, and a grounded response in seconds.
            </p>
          </div>
        </div>
        <Button asChild>
          <Link href="/complaints/new">
            Analyze now <ArrowRight className="size-4" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
