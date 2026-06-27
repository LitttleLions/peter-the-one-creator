import type {
  ActionPlanResponse,
  BookStylesResponse,
  BookNamesResponse,
  BookSettingsSaveRequest,
  BookSettingsSaveResponse,
  BooksResponse,
  ChaptersResponse,
  ExportInfoResponse,
  ExportJobRequest,
  ExtractChaptersRequest,
  IllustrationBatchRequest,
  InitBookRequest,
  JobDetail,
  JobResponse,
  JobsResponse,
  JobStartResponse,
  LogDetailResponse,
  LogsResponse,
  ModelsResponse,
  ReviewArtifactsResponse,
  ReviewFixRequest,
  ReviewJobRequest,
  SetupResponse,
  StyleTestResponse,
  TranslateBatchRequest
} from "./types";

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  return response.json() as Promise<T>;
}

export function getBooks(): Promise<BooksResponse> {
  return requestJson<BooksResponse>("/api/books");
}

export function getSetup(): Promise<SetupResponse> {
  return requestJson<SetupResponse>("/api/setup");
}

export function getChapters(bookId: string, style?: string): Promise<ChaptersResponse> {
  const params = style ? `?style=${encodeURIComponent(style)}` : "";
  return requestJson<ChaptersResponse>(`/api/books/${encodeURIComponent(bookId)}/chapters${params}`);
}

export function getBookStyles(bookId: string): Promise<BookStylesResponse> {
  return requestJson<BookStylesResponse>(`/api/books/${encodeURIComponent(bookId)}/styles`);
}

export function getBookNames(bookId: string): Promise<BookNamesResponse> {
  return requestJson<BookNamesResponse>(`/api/books/${encodeURIComponent(bookId)}/names`);
}

export function saveBookNames(bookId: string, names: unknown[]): Promise<BookNamesResponse> {
  return requestJson<BookNamesResponse>(`/api/books/${encodeURIComponent(bookId)}/names`, {
    method: "PUT",
    body: JSON.stringify({ names })
  });
}

export function saveBookSettings(bookId: string, settings: BookSettingsSaveRequest): Promise<BookSettingsSaveResponse> {
  return requestJson<BookSettingsSaveResponse>(`/api/books/${encodeURIComponent(bookId)}/settings`, {
    method: "PUT",
    body: JSON.stringify(settings)
  });
}

export function getReviewArtifacts(bookId: string, style: string): Promise<ReviewArtifactsResponse> {
  return requestJson<ReviewArtifactsResponse>(`/api/books/${encodeURIComponent(bookId)}/reviews/${encodeURIComponent(style)}`);
}

export function getExportInfo(bookId: string, style: string, scope: string, chapter?: string): Promise<ExportInfoResponse> {
  const params = new URLSearchParams({ scope });
  if (chapter) {
    params.set("chapter", chapter);
  }
  return requestJson<ExportInfoResponse>(`/api/books/${encodeURIComponent(bookId)}/exports/${encodeURIComponent(style)}?${params.toString()}`);
}

export function getStyleTest(bookId: string, chapter: string, scene?: string): Promise<StyleTestResponse> {
  const params = new URLSearchParams({ chapter });
  if (scene) {
    params.set("scene", String(Number(scene)));
  }
  return requestJson<StyleTestResponse>(`/api/books/${encodeURIComponent(bookId)}/style-test?${params.toString()}`);
}

export function getModels(): Promise<ModelsResponse> {
  return requestJson<ModelsResponse>("/api/models");
}

export function getJobs(limit = 20): Promise<JobsResponse> {
  return requestJson<JobsResponse>(`/api/jobs?limit=${limit}`);
}

export function getLogs(bookId?: string, limit = 50): Promise<LogsResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (bookId) {
    params.set("book_id", bookId);
  }
  return requestJson<LogsResponse>(`/api/logs?${params.toString()}`);
}

export function getLog(logId: string, lines = 300): Promise<LogDetailResponse> {
  return requestJson<LogDetailResponse>(`/api/logs/${encodeURIComponent(logId)}?lines=${lines}`);
}

export function getJob(jobId: string): Promise<JobResponse> {
  return requestJson<JobResponse>(`/api/jobs/${encodeURIComponent(jobId)}`);
}

export function stopJob(jobId: string): Promise<JobResponse & { stopped: boolean; message?: string }> {
  return requestJson<JobResponse & { stopped: boolean; message?: string }>(
    `/api/jobs/${encodeURIComponent(jobId)}/stop`,
    { method: "POST" }
  );
}

export function startTranslateBatchJob(payload: TranslateBatchRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function planAction(payload: TranslateBatchRequest | ReviewJobRequest | ReviewFixRequest | ExportJobRequest | IllustrationBatchRequest | InitBookRequest | ExtractChaptersRequest): Promise<ActionPlanResponse> {
  return requestJson<ActionPlanResponse>("/api/actions/plan", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startReviewJob(payload: ReviewJobRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startReviewFixJob(payload: ReviewFixRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startExportJob(payload: ExportJobRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startIllustrationBatchJob(payload: IllustrationBatchRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startActionJob(payload: InitBookRequest | ExtractChaptersRequest): Promise<JobStartResponse> {
  return requestJson<JobStartResponse>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function jobEventsUrl(jobId: string): string {
  return `/api/jobs/${encodeURIComponent(jobId)}/events`;
}

export function parseSseJobPayload(raw: string): JobDetail {
  return JSON.parse(raw) as JobDetail;
}

export function formatProgress(job?: JobDetail | null): string {
  if (!job || job.progress.done == null || job.progress.total == null) {
    return "kein Fortschritt";
  }
  return `${job.progress.done}/${job.progress.total}`;
}
