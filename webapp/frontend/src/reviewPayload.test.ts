import { describe, expect, it } from "vitest";
import { buildReviewPayload } from "./reviewPayload";

describe("buildReviewPayload", () => {
  const base = {
    bookId: "geheime-geschichte-mongolen",
    style: "stil-01-original",
    scope: "Bereich",
    chapter: "004",
    startChapter: "004",
    endChapter: "006",
    llmScope: "flagged",
    model: "deepseek/deepseek-v4-flash",
    ollamaModel: "gemma4:latest",
    failOnErrors: false
  };

  it("builds an Erstpruefung payload with llm=none and without model fields", () => {
    const payload = buildReviewPayload({ ...base, llm: "none" });
    expect(payload).toEqual({
      action: "review",
      book_id: "geheime-geschichte-mongolen",
      style: "stil-01-original",
      scope: "Bereich",
      start_chapter: "004",
      end_chapter: "006",
      llm: "none",
      llm_scope: "flagged",
      fail_on_errors: false
    });
    expect(payload).not.toHaveProperty("model");
    expect(payload).not.toHaveProperty("ollama_model");
  });

  it("builds a Deep-Check OpenRouter payload with model", () => {
    const payload = buildReviewPayload({
      ...base,
      scope: "Aktuelles Kapitel",
      llm: "openrouter",
      llmScope: "all"
    });
    expect(payload.llm).toBe("openrouter");
    expect(payload.llm_scope).toBe("all");
    expect(payload.chapter).toBe("004");
    expect(payload.model).toBe("deepseek/deepseek-v4-flash");
    expect(payload).not.toHaveProperty("ollama_model");
    expect(payload).not.toHaveProperty("start_chapter");
  });

  it("builds a Deep-Check Ollama payload with ollama_model", () => {
    const payload = buildReviewPayload({ ...base, scope: "Alle", llm: "ollama" });
    expect(payload.llm).toBe("ollama");
    expect(payload.ollama_model).toBe("gemma4:latest");
    expect(payload).not.toHaveProperty("model");
    expect(payload).not.toHaveProperty("chapter");
  });
});
