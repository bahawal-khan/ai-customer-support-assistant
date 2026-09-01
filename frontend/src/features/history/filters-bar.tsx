"use client";

import { Search, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toTitleCase } from "@/lib/format";

const INTENTS = [
  "refund_request",
  "delivery_issue",
  "payment_issue",
  "account_access",
  "cancellation_request",
  "technical_support",
  "escalation_request",
  "general_inquiry",
];
const PRIORITIES = ["low", "medium", "high", "critical"];
const SENTIMENTS = ["positive", "neutral", "negative"];

export interface HistoryFilters {
  search: string;
  intent: string;
  priority: string;
  sentiment: string;
  dateFrom: string;
  dateTo: string;
}

export const EMPTY_FILTERS: HistoryFilters = {
  search: "",
  intent: "",
  priority: "",
  sentiment: "",
  dateFrom: "",
  dateTo: "",
};

function FilterSelect({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  placeholder: string;
}) {
  return (
    <Select value={value || "all"} onValueChange={(v) => onChange(v === "all" ? "" : v)}>
      <SelectTrigger className="w-full sm:w-40">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All {placeholder}</SelectItem>
        {options.map((option) => (
          <SelectItem key={option} value={option}>
            {toTitleCase(option)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export function FiltersBar({
  filters,
  onChange,
}: {
  filters: HistoryFilters;
  onChange: (filters: HistoryFilters) => void;
}) {
  const hasActiveFilters =
    filters.search || filters.intent || filters.priority || filters.sentiment || filters.dateFrom || filters.dateTo;

  return (
    <div className="flex flex-col gap-3">
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          placeholder="Search complaint text..."
          className="pl-8"
          aria-label="Search complaints"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <FilterSelect
          value={filters.intent}
          onChange={(v) => onChange({ ...filters, intent: v })}
          options={INTENTS}
          placeholder="Intent"
        />
        <FilterSelect
          value={filters.priority}
          onChange={(v) => onChange({ ...filters, priority: v })}
          options={PRIORITIES}
          placeholder="Priority"
        />
        <FilterSelect
          value={filters.sentiment}
          onChange={(v) => onChange({ ...filters, sentiment: v })}
          options={SENTIMENTS}
          placeholder="Sentiment"
        />

        <Input
          type="date"
          value={filters.dateFrom}
          onChange={(e) => onChange({ ...filters, dateFrom: e.target.value })}
          className="w-full sm:w-auto"
          aria-label="From date"
        />
        <Input
          type="date"
          value={filters.dateTo}
          onChange={(e) => onChange({ ...filters, dateTo: e.target.value })}
          className="w-full sm:w-auto"
          aria-label="To date"
        />

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={() => onChange(EMPTY_FILTERS)}>
            <X className="size-3.5" />
            Clear
          </Button>
        )}
      </div>
    </div>
  );
}
