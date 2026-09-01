export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

export function formatShortDate(iso: string): string {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(iso));
}

export function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffMinutes = Math.round(diffMs / 60000);
  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.round(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return formatShortDate(iso);
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function toTitleCase(value: string): string {
  return value
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
}

export function truncate(value: string, max: number): string {
  if (value.length <= max) return value;
  return `${value.slice(0, max - 1).trimEnd()}…`;
}

export type PriorityLevel = "low" | "medium" | "high" | "critical";
export type SentimentLabel = "positive" | "neutral" | "negative";

export const PRIORITY_TONE: Record<string, "success" | "info" | "warning" | "destructive"> = {
  low: "success",
  medium: "info",
  high: "warning",
  critical: "destructive",
};

export const SENTIMENT_TONE: Record<string, "success" | "info" | "destructive"> = {
  positive: "success",
  neutral: "info",
  negative: "destructive",
};
