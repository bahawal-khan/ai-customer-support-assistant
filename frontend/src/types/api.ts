/**
 * Types mirror backend/app/schemas/*.py exactly (docs/api/API_SPEC.md).
 * Keep in sync with the Pydantic response models until Task 14 generates
 * these from the OpenAPI schema.
 */

export interface IntentResult {
  label: string;
  confidence: number;
  model_version: string;
}

export interface SentimentResult {
  label: string;
  confidence: number;
}

export interface PriorityResult {
  level: "low" | "medium" | "high" | "critical" | (string & {});
  reason: string;
}

export interface RetrievedSource {
  chunk_id: string | null;
  document_id: string | null;
  source_id: string;
  title: string;
  category: string;
  version: string;
  chunk_index: number;
  content: string;
  score: number;
  rank: number;
}

export interface ModelMetadata {
  intent_model_version: string;
  embedding_model: string;
  llm_provider: string | null;
  llm_model: string | null;
  prompt_version: string | null;
  retrieved_source_count: number;
  llm_available: boolean;
}

export interface ComplaintAnalyzeResponse {
  request_id: string;
  complaint_id: string;
  intent: IntentResult;
  sentiment: SentimentResult;
  priority: PriorityResult;
  retrieved_sources: RetrievedSource[];
  suggested_response: string | null;
  model_metadata: ModelMetadata;
}

export interface ComplaintDetailResponse {
  complaint_id: string;
  text: string;
  created_at: string;
  intent: IntentResult;
  sentiment: SentimentResult;
  priority: PriorityResult;
  retrieved_sources: RetrievedSource[];
  suggested_response: string | null;
  model_metadata: ModelMetadata;
}

export interface ComplaintHistoryItem {
  complaint_id: string;
  text: string;
  intent: string;
  intent_confidence: number;
  sentiment: string;
  sentiment_confidence: number;
  priority: string;
  created_at: string;
}

export interface PaginatedComplaints {
  items: ComplaintHistoryItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface ComplaintBulkDeleteResponse {
  deleted_ids: string[];
}

export interface ComplaintHistoryQuery {
  page?: number;
  page_size?: number;
  search?: string;
  intent?: string;
  priority?: string;
  sentiment?: string;
  date_from?: string;
  date_to?: string;
}

export type DocumentStatus = "pending" | "indexed" | "failed" | (string & {});

export interface DocumentOut {
  id: string;
  source_id: string;
  title: string;
  category: string;
  version: string;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
  chunk_count: number;
}

export interface DocumentListResponse {
  items: DocumentOut[];
  total: number;
}

export interface DocumentIndexResponse {
  document_id: string;
  source_id: string;
  action: string;
  chunk_count: number;
  status: string;
}

export interface DocumentDeleteResponse {
  document_id: string;
  deleted: boolean;
}

export interface HealthResponse {
  status: string;
  database: string;
  version: string;
}

/** docs/api/API_SPEC.md "Error contract". */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
  };
}

export class ApiError extends Error {
  code: string;
  requestId: string;
  status: number;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = body.error.code;
    this.requestId = body.error.request_id;
  }
}
