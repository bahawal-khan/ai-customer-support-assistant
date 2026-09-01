import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { toTitleCase } from "@/lib/format";

export type StatusTone = "success" | "info" | "warning" | "destructive" | "neutral";

const TONE_CLASSES: Record<StatusTone, string> = {
  success: "bg-success/10 text-success dark:bg-success/15",
  info: "bg-info/10 text-info dark:bg-info/15",
  warning: "bg-warning/15 text-warning-foreground dark:bg-warning/20 dark:text-warning",
  destructive: "bg-destructive/10 text-destructive dark:bg-destructive/20",
  neutral: "bg-muted text-muted-foreground",
};

export function StatusBadge({
  tone,
  label,
  className,
}: {
  tone: StatusTone;
  label: string;
  className?: string;
}) {
  return (
    <Badge variant="outline" className={cn("border-transparent font-medium", TONE_CLASSES[tone], className)}>
      {toTitleCase(label)}
    </Badge>
  );
}
