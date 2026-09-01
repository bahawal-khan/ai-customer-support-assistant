"use client";

import * as React from "react";
import { toast } from "sonner";

import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/error-state";
import { FiltersBar, EMPTY_FILTERS, type HistoryFilters } from "@/features/history/filters-bar";
import { ComplaintsTable } from "@/features/history/complaints-table";
import { SelectionToolbar } from "@/features/history/selection-toolbar";
import { Pagination } from "@/features/history/pagination";
import { deleteComplaints, listComplaints } from "@/lib/api/client";
import { ApiError, type PaginatedComplaints } from "@/types/api";

const PAGE_SIZE = 8;
const SEARCH_DEBOUNCE_MS = 300;

export function HistoryView() {
  const [filters, setFilters] = React.useState<HistoryFilters>(EMPTY_FILTERS);
  const [debouncedSearch, setDebouncedSearch] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [data, setData] = React.useState<PaginatedComplaints | null>(null);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [reloadKey, setReloadKey] = React.useState(0);
  const [selectedIds, setSelectedIds] = React.useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = React.useState(false);

  React.useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(filters.search), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timeout);
  }, [filters.search]);

  // Reset to page 1 whenever the effective query changes, computed during
  // render per https://react.dev/learn/you-might-not-need-an-effect
  // (adjusting state when a prop/derived value changes) rather than in an
  // effect, since the latter causes an extra render pass.
  const queryKey = [debouncedSearch, filters.intent, filters.priority, filters.sentiment, filters.dateFrom, filters.dateTo].join(
    "|"
  );
  const [prevQueryKey, setPrevQueryKey] = React.useState(queryKey);
  if (queryKey !== prevQueryKey) {
    setPrevQueryKey(queryKey);
    setPage(1);
  }

  React.useEffect(() => {
    let active = true;
    listComplaints({
      page,
      page_size: PAGE_SIZE,
      search: debouncedSearch || undefined,
      intent: filters.intent || undefined,
      priority: filters.priority || undefined,
      sentiment: filters.sentiment || undefined,
      date_from: filters.dateFrom || undefined,
      date_to: filters.dateTo || undefined,
    })
      .then((result) => {
        if (!active) return;
        setData(result);
        setLoadError(null);
      })
      .catch((err) => {
        if (!active) return;
        setLoadError(err instanceof ApiError ? err.message : "Couldn't load complaint history.");
      });
    return () => {
      active = false;
    };
  }, [
    page,
    debouncedSearch,
    filters.intent,
    filters.priority,
    filters.sentiment,
    filters.dateFrom,
    filters.dateTo,
    reloadKey,
  ]);

  // Selection is scoped to the current page/query: whenever the underlying
  // rows change (page, filters, or a reload after a successful delete), any
  // previously selected IDs may no longer be visible, so drop them. Computed
  // during render (see the queryKey/prevQueryKey pattern above) rather than
  // in an effect, to avoid an extra render pass.
  const selectionResetKey = `${queryKey}|${page}|${reloadKey}`;
  const [prevSelectionResetKey, setPrevSelectionResetKey] = React.useState(selectionResetKey);
  if (selectionResetKey !== prevSelectionResetKey) {
    setPrevSelectionResetKey(selectionResetKey);
    setSelectedIds(new Set());
  }

  function toggleRow(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function toggleAll() {
    if (!data) return;
    setSelectedIds((prev) => {
      const allSelected = data.items.every((item) => prev.has(item.complaint_id));
      return allSelected ? new Set() : new Set(data.items.map((item) => item.complaint_id));
    });
  }

  async function handleDeleteSelected() {
    const ids = Array.from(selectedIds);
    setIsDeleting(true);
    try {
      await deleteComplaints(ids);
      toast.success(`${ids.length} complaint${ids.length === 1 ? "" : "s"} deleted`);
      setReloadKey((k) => k + 1);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Couldn't delete the selected complaints."
      );
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">History</h1>
        <p className="text-sm text-muted-foreground">Search and filter previously analyzed complaints.</p>
      </div>

      <FiltersBar filters={filters} onChange={setFilters} />

      {loadError ? (
        <ErrorState message={loadError} onRetry={() => setReloadKey((k) => k + 1)} />
      ) : data === null ? (
        <Skeleton className="h-96 rounded-xl" />
      ) : (
        <>
          <SelectionToolbar
            count={selectedIds.size}
            isDeleting={isDeleting}
            onDelete={handleDeleteSelected}
          />
          <ComplaintsTable
            items={data.items}
            selectedIds={selectedIds}
            onToggleRow={toggleRow}
            onToggleAll={toggleAll}
          />
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
