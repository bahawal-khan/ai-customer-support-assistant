"use client";

import * as React from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/error-state";
import { UploadDialog } from "@/features/knowledge-base/upload-dialog";
import { DocumentsTable } from "@/features/knowledge-base/documents-table";
import { listDocuments } from "@/lib/api/client";
import { ApiError, type DocumentOut } from "@/types/api";

export function KnowledgeView() {
  const [documents, setDocuments] = React.useState<DocumentOut[] | null>(null);
  const [loadError, setLoadError] = React.useState<string | null>(null);

  const refresh = React.useCallback(() => {
    listDocuments()
      .then((result) => {
        setDocuments(result.items);
        setLoadError(null);
      })
      .catch((err) => {
        setLoadError(err instanceof ApiError ? err.message : "Couldn't load knowledge documents.");
      });
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  const indexedCount = documents?.filter((d) => d.status === "indexed").length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge Base</h1>
          <p className="text-sm text-muted-foreground">
            {documents ? `${indexedCount} of ${documents.length} documents indexed` : "Loading documents..."}
          </p>
        </div>
        <UploadDialog onUploaded={refresh} />
      </div>

      {loadError ? (
        <ErrorState message={loadError} onRetry={refresh} />
      ) : documents === null ? (
        <Skeleton className="h-96 rounded-xl" />
      ) : (
        <DocumentsTable documents={documents} onChanged={refresh} />
      )}
    </div>
  );
}
