import { afterEach, describe, expect, it, vi } from "vitest";
import { formatProgress, getBookNames, getLog, getLogs, jobEventsUrl, parseSseJobPayload, planAction, saveBookSettings, startExportJob, startReviewJob, startTranslateBatchJob } from "./api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("api helpers", () => {
  it("builds encoded event urls", () => {
    expect(jobEventsUrl("job 1/review")).toBe("/api/jobs/job%201%2Freview/events");
  });

  it("formats progress when available", () => {
    expect(formatProgress({
      job_id: "x",
      status: "running",
      running: true,
      progress: { done: 2, total: 5 }
    })).toBe("2/5");
  });

  it("parses sse job payload", () => {
    const job = parseSseJobPayload('{"job_id":"abc","status":"completed","running":false,"progress":{"done":1,"total":1}}');
    expect(job.job_id).toBe("abc");
    expect(job.progress.done).toBe(1);
  });

  it("starts translate batch jobs through the backend", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        job: { job_id: "job-1", status: "running", running: true, progress: { done: null, total: null } },
        command: ["tools/translate_batch.py"]
      })
    } as Response);

    const result = await startTranslateBatchJob({
      action: "translate_batch",
      book_id: "pharao",
      style: "stil-02-poetisch",
      provider: "openrouter",
      scope: "Aktuelles Kapitel",
      chapter: "002",
      model: "anthropic/claude-sonnet-4.6",
      auto_status: true,
      assemble_after: true
    });

    expect(result.job.job_id).toBe("job-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs", expect.objectContaining({
      method: "POST",
      body: expect.stringContaining('"chapter":"002"')
    }));
  });

  it("starts single scene translation jobs through the backend", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        job: { job_id: "scene-1", status: "running", running: true, progress: { done: null, total: null } },
        command: ["tools/translate_chapter.py", "--scene", "01"]
      })
    } as Response);

    const result = await startTranslateBatchJob({
      action: "translate_chapter",
      book_id: "pharao",
      style: "stil-02-poetisch",
      provider: "openrouter",
      scope: "Einzelne Szene",
      chapter: "002",
      scene: "01",
      model: "anthropic/claude-sonnet-4.6"
    });

    expect(result.job.job_id).toBe("scene-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs", expect.objectContaining({
      method: "POST",
      body: expect.stringContaining('"scene":"01"')
    }));
  });

  it("plans translate dry-runs through the backend", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        action: "translate_batch",
        command: ["tools/translate_batch.py", "--dry-run"],
        command_text: "tools/translate_batch.py --dry-run",
        cwd: "."
      })
    } as Response);

    const result = await planAction({
      action: "translate_batch",
      book_id: "pharao",
      style: "stil-02-poetisch",
      provider: "openrouter",
      scope: "Aktuelles Kapitel",
      chapter: "002",
      dry_run: true
    });

    expect(result.command_text).toContain("--dry-run");
    expect(fetchMock).toHaveBeenCalledWith("/api/actions/plan", expect.objectContaining({
      method: "POST",
      body: expect.stringContaining('"dry_run":true')
    }));
  });

  it("starts review jobs through the backend", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        job: { job_id: "review-1", status: "running", running: true, progress: { done: null, total: null } },
        command: ["tools/review_manuscript.py"]
      })
    } as Response);

    const result = await startReviewJob({
      action: "review",
      book_id: "pharao",
      style: "stil-02-poetisch",
      scope: "Aktuelles Kapitel",
      chapter: "002",
      llm: "ollama",
      llm_scope: "flagged",
      ollama_model: "gemma4:latest"
    });

    expect(result.job.job_id).toBe("review-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs", expect.objectContaining({
      method: "POST",
      body: expect.stringContaining('"action":"review"')
    }));
  });

  it("starts export jobs through the backend", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        job: { job_id: "export-1", status: "running", running: true, progress: { done: null, total: null } },
        command: ["tools/export_manuscript.py"]
      })
    } as Response);

    const result = await startExportJob({
      action: "export",
      book_id: "pharao",
      style: "stil-02-poetisch",
      scope: "chapter",
      chapter: "002",
      export_format: "pdf",
      allow_partial: true
    });

    expect(result.job.job_id).toBe("export-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs", expect.objectContaining({
      method: "POST",
      body: expect.stringContaining('"export_format":"pdf"')
    }));
  });

  it("loads book names", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        book_id: "pharao",
        names: [{ source: "Rameses", target: "Ramses", aliases: "", type: "person", status: "approved", note: "" }]
      })
    } as Response);

    const result = await getBookNames("pharao");

    expect(result.names[0].target).toBe("Ramses");
    expect(fetchMock).toHaveBeenCalledWith("/api/books/pharao/names", expect.objectContaining({
      headers: { "Content-Type": "application/json" }
    }));
  });

  it("saves book settings", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        book_id: "pharao",
        saved: true,
        summary: {
          id: "pharao",
          title: "Der Pharao",
          style_mode: "stil-02-poetisch",
          chapters: 1,
          missing_scenes: 0
        },
        book: {}
      })
    } as Response);

    const result = await saveBookSettings("pharao", {
      active_style: "stil-02-poetisch",
      translate_provider: "openrouter",
      translate_model: "deepseek/deepseek-v4-pro",
      chunk_char_limit: 12000
    });

    expect(result.saved).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith("/api/books/pharao/settings", expect.objectContaining({
      method: "PUT",
      body: expect.stringContaining('"active_style":"stil-02-poetisch"')
    }));
  });

  it("loads logs and log details", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          logs: [{ id: "abc", path: "var/dashboard-jobs/job.log", name: "job.log", source: "dashboard-job", size: 20, modified_at: "2026-06-24T08:00:00" }]
        })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          log: { id: "abc", path: "var/dashboard-jobs/job.log", name: "job.log", source: "dashboard-job", size: 20, modified_at: "2026-06-24T08:00:00" },
          content: "line",
          truncated: false
        })
      } as Response);

    const logs = await getLogs("pharao", 10);
    const detail = await getLog("abc", 5);

    expect(logs.logs[0].name).toBe("job.log");
    expect(detail.content).toBe("line");
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/api/logs?limit=10&book_id=pharao", expect.any(Object));
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/logs/abc?lines=5", expect.any(Object));
  });
});
