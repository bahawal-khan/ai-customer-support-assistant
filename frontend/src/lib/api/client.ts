import {
  ApiError,
  type ApiErrorBody,
  type ComplaintAnalyzeResponse,
  type ComplaintBulkDeleteResponse,
  type ComplaintDetailResponse,
  type ComplaintHistoryQuery,
  type DocumentDeleteResponse,
  type DocumentIndexResponse,
  type DocumentListResponse,
  type DocumentOut,
  type HealthResponse,
  type PaginatedComplaints,
} from "@/types/api";

/** Typed client for docs/api/API_SPEC.md, used by every feature view (lib/ - API client per docs/frontend/FRONTEND_ARCHITECTURE.md). */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
    if (body?.error) {
      throw new ApiError(response.status, body);
    }
    throw new ApiError(response.status, {
      error: { code: "unknown_error", message: response.statusText, request_id: "" },
    });
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function analyzeComplaint(text: string): Promise<ComplaintAnalyzeResponse> {
  return request<ComplaintAnalyzeResponse>("/complaints/analyze", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function listComplaints(query: ComplaintHistoryQuery = {}): Promise<PaginatedComplaints> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return request<PaginatedComplaints>(`/complaints${qs ? `?${qs}` : ""}`);
}

export function getComplaint(id: string): Promise<ComplaintDetailResponse> {
  return request<ComplaintDetailResponse>(`/complaints/${id}`);
}

export function deleteComplaints(complaintIds: string[]): Promise<ComplaintBulkDeleteResponse> {
  return request<ComplaintBulkDeleteResponse>("/complaints", {
    method: "DELETE",
    body: JSON.stringify({ complaint_ids: complaintIds }),
  });
}

export function listDocuments(): Promise<DocumentListResponse> {
  return request<DocumentListResponse>("/knowledge/documents");
}

export function uploadDocument(file: File): Promise<DocumentOut> {
  const formData = new FormData();
  formData.set("file", file);
  return request<DocumentOut>("/knowledge/documents", {
    method: "POST",
    body: formData,
  });
}

export function indexDocument(documentId: string): Promise<DocumentIndexResponse> {
  return request<DocumentIndexResponse>(`/knowledge/documents/${documentId}/index`, {
    method: "POST",
  });
}

export function deleteDocument(documentId: string): Promise<DocumentDeleteResponse> {
  return request<DocumentDeleteResponse>(`/knowledge/documents/${documentId}`, {
    method: "DELETE",
  });
}
