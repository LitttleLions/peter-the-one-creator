import type { ReviewJobRequest } from "./types";

export function buildReviewPayload(options: {
  bookId: string;
  style: string;
  scope: string;
  chapter: string;
  startChapter: string;
  endChapter: string;
  llm: string;
  llmScope: string;
  model: string;
  ollamaModel: string;
  failOnErrors: boolean;
}): ReviewJobRequest {
  const payload: ReviewJobRequest = {
    action: "review",
    book_id: options.bookId,
    style: options.style,
    scope: options.scope,
    llm: options.llm,
    llm_scope: options.llmScope,
    fail_on_errors: options.failOnErrors
  };
  if (options.scope === "Aktuelles Kapitel") {
    payload.chapter = options.chapter;
  }
  if (options.scope === "Bereich") {
    payload.start_chapter = options.startChapter;
    payload.end_chapter = options.endChapter;
  }
  if (options.llm === "openrouter") {
    payload.model = options.model;
  }
  if (options.llm === "ollama") {
    payload.ollama_model = options.ollamaModel;
  }
  return payload;
}
