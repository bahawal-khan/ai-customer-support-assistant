"use client";

import * as React from "react";
import { RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { StatusBadge, type StatusTone } from "@/components/status-badge";
import { formatDate, toTitleCase } from "@/lib/format";
import { deleteDocument, indexDocument } from "@/lib/api/client";
import type { DocumentOut } from "@/types/api";

const STATUS_TONE: Record<string, StatusTone> = {
  indexed: "success",
  pending: "warning",
  failed: "destructive",
};

export function DocumentsTable({
  documents,
  onChanged,
}: {
  documents: DocumentOut[];
  onChanged: () => void;
}) {
  const [pendingAction, setPendingAction] = React.useState<string | null>(null);

  async function handleReindex(doc: DocumentOut) {
    setPendingAction(doc.id);
    try {
      await indexDocument(doc.id);
      toast.success(`${doc.title} re-indexed`);
      onChanged();
    } catch {
      toast.error("Re-index failed");
    } finally {
      setPendingAction(null);
    }
  }

  async function handleDelete(doc: DocumentOut) {
    setPendingAction(doc.id);
    try {
      await deleteDocument(doc.id);
      toast.success(`${doc.title} deleted`);
      onChanged();
    } catch {
      toast.error("Delete failed");
    } finally {
      setPendingAction(null);
    }
  }

  if (documents.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border py-16 text-center text-sm text-muted-foreground">
        No knowledge documents yet. Upload one to get started.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Version</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Chunks</TableHead>
            <TableHead>Updated</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((doc) => (
            <TableRow key={doc.id}>
              <TableCell className="font-medium">{doc.title}</TableCell>
              <TableCell>{toTitleCase(doc.category)}</TableCell>
              <TableCell className="text-muted-foreground">{doc.version}</TableCell>
              <TableCell>
                <StatusBadge tone={STATUS_TONE[doc.status] ?? "neutral"} label={doc.status} />
              </TableCell>
              <TableCell className="tabular-nums text-muted-foreground">{doc.chunk_count ?? 0}</TableCell>
              <TableCell className="text-muted-foreground">{formatDate(doc.updated_at)}</TableCell>
              <TableCell>
                <div className="flex justify-end gap-1.5">
                  <Button
                    variant="outline"
                    size="icon-sm"
                    aria-label={`Re-index ${doc.title}`}
                    disabled={pendingAction === doc.id}
                    onClick={() => handleReindex(doc)}
                  >
                    <RefreshCw className={`size-3.5 ${pendingAction === doc.id ? "animate-spin" : ""}`} />
                  </Button>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="icon-sm" aria-label={`Delete ${doc.title}`}>
                        <Trash2 className="size-3.5 text-destructive" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete &ldquo;{doc.title}&rdquo;?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This removes the document and its indexed chunks. This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          onClick={() => handleDelete(doc)}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
