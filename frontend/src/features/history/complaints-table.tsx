"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { StatusBadge } from "@/components/status-badge";
import { PRIORITY_TONE, SENTIMENT_TONE, formatDate, toTitleCase, truncate } from "@/lib/format";
import type { ComplaintHistoryItem } from "@/types/api";

type SortKey = "text" | "intent" | "priority" | "sentiment" | "created_at";
type SortDirection = "asc" | "desc";

const PRIORITY_ORDER: Record<string, number> = { low: 0, medium: 1, high: 2, critical: 3 };

function SortHeader({
  label,
  sortKeyValue,
  activeKey,
  direction,
  onToggle,
}: {
  label: string;
  sortKeyValue: SortKey;
  activeKey: SortKey;
  direction: SortDirection;
  onToggle: (key: SortKey) => void;
}) {
  const isActive = activeKey === sortKeyValue;
  const Icon = isActive ? (direction === "asc" ? ArrowUp : ArrowDown) : ArrowUpDown;
  return (
    <button
      type="button"
      onClick={() => onToggle(sortKeyValue)}
      className="flex items-center gap-1 text-left font-medium hover:text-foreground"
    >
      {label}
      <Icon className={`size-3.5 ${isActive ? "text-foreground" : "text-muted-foreground/60"}`} />
    </button>
  );
}

export function ComplaintsTable({
  items,
  selectedIds,
  onToggleRow,
  onToggleAll,
}: {
  items: ComplaintHistoryItem[];
  selectedIds: Set<string>;
  onToggleRow: (id: string) => void;
  onToggleAll: () => void;
}) {
  const router = useRouter();
  const [sortKey, setSortKey] = React.useState<SortKey>("created_at");
  const [sortDirection, setSortDirection] = React.useState<SortDirection>("desc");

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }
  }

  const sorted = React.useMemo(() => {
    const copy = [...items];
    copy.sort((a, b) => {
      let comparison = 0;
      if (sortKey === "priority") {
        comparison = (PRIORITY_ORDER[a.priority] ?? 0) - (PRIORITY_ORDER[b.priority] ?? 0);
      } else {
        comparison = a[sortKey].localeCompare(b[sortKey]);
      }
      return sortDirection === "asc" ? comparison : -comparison;
    });
    return copy;
  }, [items, sortKey, sortDirection]);

  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border py-16 text-center text-sm text-muted-foreground">
        No complaints match the current filters.
      </div>
    );
  }

  const allSelected = items.every((item) => selectedIds.has(item.complaint_id));
  const someSelected = items.some((item) => selectedIds.has(item.complaint_id));

  return (
    <div className="rounded-xl border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-10">
              <Checkbox
                checked={allSelected ? true : someSelected ? "indeterminate" : false}
                onCheckedChange={onToggleAll}
                aria-label="Select all complaints on this page"
              />
            </TableHead>
            <TableHead>
              <SortHeader
                label="Complaint"
                sortKeyValue="text"
                activeKey={sortKey}
                direction={sortDirection}
                onToggle={toggleSort}
              />
            </TableHead>
            <TableHead>
              <SortHeader
                label="Intent"
                sortKeyValue="intent"
                activeKey={sortKey}
                direction={sortDirection}
                onToggle={toggleSort}
              />
            </TableHead>
            <TableHead>
              <SortHeader
                label="Sentiment"
                sortKeyValue="sentiment"
                activeKey={sortKey}
                direction={sortDirection}
                onToggle={toggleSort}
              />
            </TableHead>
            <TableHead>
              <SortHeader
                label="Priority"
                sortKeyValue="priority"
                activeKey={sortKey}
                direction={sortDirection}
                onToggle={toggleSort}
              />
            </TableHead>
            <TableHead>
              <SortHeader
                label="Date"
                sortKeyValue="created_at"
                activeKey={sortKey}
                direction={sortDirection}
                onToggle={toggleSort}
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((row) => (
            <TableRow
              key={row.complaint_id}
              className="cursor-pointer"
              onClick={() => router.push(`/complaints/${row.complaint_id}`)}
            >
              <TableCell onClick={(e) => e.stopPropagation()}>
                <Checkbox
                  checked={selectedIds.has(row.complaint_id)}
                  onCheckedChange={() => onToggleRow(row.complaint_id)}
                  aria-label={`Select complaint: ${truncate(row.text, 40)}`}
                />
              </TableCell>
              <TableCell className="max-w-xs whitespace-normal font-medium">
                {truncate(row.text, 90)}
              </TableCell>
              <TableCell>{toTitleCase(row.intent)}</TableCell>
              <TableCell>
                <StatusBadge tone={SENTIMENT_TONE[row.sentiment] ?? "neutral"} label={row.sentiment} />
              </TableCell>
              <TableCell>
                <StatusBadge tone={PRIORITY_TONE[row.priority] ?? "neutral"} label={row.priority} />
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(row.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
