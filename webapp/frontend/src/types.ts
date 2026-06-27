export type BookSummary = {
  id: string;
  title: string;
  author?: string;
  source_lang?: string;
  target_lang?: string;
  style_mode: string;
  ai_provider?: string;
  ai_model?: string;
  chunk_char_limit?: number;
  chapters: number;
  missing_scenes: number;
  book_root?: string;
};

export type WorkspaceSettings = {
  active_style: string;
  translate_provider: string;
  translate_model: string;
  translate_ollama_model: string;
  chunk_char_limit: number;
  review_llm: string;
  review_llm_scope: string;
  review_model: string;
  review_ollama_model: string;
  export_format: string;
};

export type ChapterRow = {
  Kapitel: string;
  Status?: string;
  "Titel RU"?: string;
  RU: number;
  DE: number;
  Fehlt: number;
  "Naechste Szene"?: string;
  Assemblies?: number;
};

export type JobProgress = {
  done: number | null;
  total: number | null;
};

export type JobDetail = {
  job_id: string;
  status: string;
  running: boolean;
  book_id?: string;
  style?: string;
  provider?: string;
  kind?: string;
  started_at?: string;
  updated_at?: string;
  completed_at?: string;
  log_path?: string;
  log_tail?: string;
  progress: JobProgress;
};

export type StyleOption = {
  id: string;
  label: string;
};

export type ModelOption = {
  id: string;
  name?: string;
  provider?: string;
  description?: string;
};

export type NameRow = {
  source: string;
  target: string;
  aliases: string;
  type: string;
  status: string;
  note: string;
  visual: string;
  character_id: string;
};

export type LogItem = {
  id: string;
  path: string;
  name: string;
  source: string;
  size: number;
  modified_at: string;
};

export type TranslateBatchRequest = {
  action: "translate_batch" | "translate_chapter";
  book_id: string;
  style: string;
  provider: string;
  scope: string;
  chapter?: string;
  start_chapter?: string;
  end_chapter?: string;
  scene?: string;
  model?: string;
  ollama_model?: string;
  chunk_char_limit?: number;
  overwrite?: boolean;
  auto_status?: boolean;
  assemble_after?: boolean;
  dry_run?: boolean;
};

export type InitBookRequest = {
  action: "init_book";
  source: string;
  title: string;
  author?: string;
  style: string;
  source_lang: string;
  target_lang: string;
  ruleset_apply?: boolean;
};

export type ExtractChaptersRequest = {
  action: "extract_chapters";
  book_id: string;
};

export type ActionPlanResponse = {
  action: string;
  command: string[];
  command_text: string;
  cwd: string;
};

export type ReviewJobRequest = {
  action: "review";
  book_id: string;
  style: string;
  scope: string;
  chapter?: string;
  start_chapter?: string;
  end_chapter?: string;
  llm: string;
  llm_scope: string;
  model?: string;
  ollama_model?: string;
  fail_on_errors?: boolean;
};

export type ReviewFixRequest = {
  action: "review_fixes";
  book_id: string;
  style: string;
  fix_action: "plan" | "stage" | "promote";
};

export type ExportJobRequest = {
  action: "export";
  book_id: string;
  style: string;
  scope: string;
  chapter?: string;
  export_format: string;
  allow_partial?: boolean;
};

export type ExportContext = {
  output_root: string;
  cover_status: string;
  illustrations_status: string;
  front_enabled: string[];
  chapter_metrics: {
    scope: string;
    chapter: string;
    chapters: number;
    source_label: string;
    source_scenes: number;
    de_scenes: number;
    missing: number;
    missing_scenes: string[];
  };
  missing_chapters: string[];
  selected_chapters: string[];
  illustration_counts: {
    chapter: number;
    scene: number;
    total: number;
  };
};

export type ExportInfoResponse = {
  book_id: string;
  style: string;
  scope: string;
  chapter: string;
  context: ExportContext;
  latest_files: ReviewFileInfo[];
};

export type IllustrationBatchRequest = {
  action: "illustration_batch";
  book_id: string;
  style: string;
  kind: "scene" | "chapter" | "both";
  scope: "chapter" | "range";
  chapter?: string;
  start_chapter?: string;
  end_chapter?: string;
  backend?: "cli" | "api" | "auto";
  model?: string;
  moodboard?: string;
  aspect_ratio?: string;
  quality?: string;
  missing?: boolean;
  overwrite?: boolean;
  dry_run?: boolean;
  no_reference?: boolean;
  allow_paid_generation?: boolean;
};

export type BooksResponse = {
  books: BookSummary[];
};

export type ChaptersResponse = {
  book_id: string;
  style: string;
  chapters: ChapterRow[];
};

export type JobsResponse = {
  jobs: JobDetail[];
};

export type JobResponse = {
  job: JobDetail;
};

export type BookStylesResponse = {
  book_id: string;
  default_style: string;
  styles: StyleOption[];
};

export type BookNamesResponse = {
  book_id: string;
  names: NameRow[];
  saved?: boolean;
};

export type BookSettingsSaveRequest = {
  active_style: string;
  translate_provider: string;
  translate_model?: string;
  chunk_char_limit?: number;
};

export type BookSettingsSaveResponse = {
  book_id: string;
  saved: boolean;
  summary: BookSummary;
  book: Record<string, unknown>;
};

export type ReviewFileInfo = {
  path: string;
  name: string;
  size: number;
  modified_at: string;
};

export type StyleTestArtifact = {
  path?: ReviewFileInfo | null;
  content: string;
};

export type StyleTestStyleResult = {
  id: string;
  label: string;
  scene: StyleTestArtifact;
  prompt: StyleTestArtifact;
  has_output: boolean;
};

export type StyleTestResponse = {
  book_id: string;
  chapter: string;
  source_lang: string;
  scenes: string[];
  selected_scene?: string | null;
  source?: StyleTestArtifact | null;
  styles: StyleTestStyleResult[];
};

export type ReviewReport = {
  chapter: string;
  markdown?: ReviewFileInfo | null;
  json?: ReviewFileInfo | null;
  content: string;
  data?: Record<string, unknown> | null;
};

export type ReviewFixArtifact = {
  file?: ReviewFileInfo | null;
  content: string;
  data?: Record<string, unknown> | null;
};

export type ReviewArtifactsResponse = {
  book_id: string;
  style: string;
  exists: boolean;
  review_root: string;
  summary?: Record<string, unknown> | null;
  summary_markdown: string;
  summary_file?: ReviewFileInfo | null;
  summary_json_file?: ReviewFileInfo | null;
  reports: ReviewReport[];
  fixes: {
    manifest: ReviewFixArtifact;
    plan: ReviewFixArtifact;
    manual_review: ReviewFixArtifact;
    promotion_report: ReviewFixArtifact;
  };
};

export type ModelsResponse = {
  models: ModelOption[];
};

export type SetupSource = {
  path: string;
  name: string;
  title: string;
  author: string;
};

export type SetupResponse = {
  unregistered_sources: SetupSource[];
  styles: StyleOption[];
  metadata_prompt: string;
  books: BookSummary[];
};

export type LogsResponse = {
  logs: LogItem[];
};

export type LogDetailResponse = {
  log: LogItem;
  content: string;
  truncated: boolean;
};

export type JobStartResponse = JobResponse & {
  command: string[];
};
