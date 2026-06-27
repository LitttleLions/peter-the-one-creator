import { useEffect, useMemo, useState, type ReactNode } from "react";
import { NavLink, Navigate, Route, Routes, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  BookOpen,
  FileText,
  Home,
  Image,
  Languages,
  ListChecks,
  Menu,
  NotebookTabs,
  PauseCircle,
  RefreshCw,
  ScrollText,
  Settings,
  Square,
  X
} from "lucide-react";
import {
  formatProgress,
  getBooks,
  getBookNames,
  getBookStyles,
  getChapters,
  getExportInfo,
  getJob,
  getJobs,
  getLog,
  getLogs,
  getModels,
  getReviewArtifacts,
  getSetup,
  getStyleTest,
  jobEventsUrl,
  planAction,
  parseSseJobPayload,
  saveBookNames,
  saveBookSettings,
  startActionJob,
  startExportJob,
  startIllustrationBatchJob,
  startReviewFixJob,
  startReviewJob,
  startTranslateBatchJob,
  stopJob
} from "./api";
import type { BookSummary, ChapterRow, ExportJobRequest, ExtractChaptersRequest, IllustrationBatchRequest, InitBookRequest, JobDetail, LogItem, NameRow, ReviewFixRequest, ReviewJobRequest, TranslateBatchRequest } from "./types";
import type { WorkspaceSettings } from "./types";

const navItems = [
  { label: "Uebersicht", path: "overview", icon: Home },
  { label: "Uebersetzen", path: "translate", icon: Languages },
  { label: "Stiltest", path: "style-test", icon: Activity },
  { label: "Review", path: "review", icon: ListChecks },
  { label: "Export", path: "export", icon: FileText },
  { label: "Bilder", path: "images", icon: Image },
  { label: "Namen", path: "names", icon: NotebookTabs },
  { label: "Logs", path: "logs", icon: ScrollText },
  { label: "Buch-Settings", path: "settings", icon: Settings }
];

const FALLBACK_OPENROUTER_MODEL = "deepseek/deepseek-v4-pro";
const JOBS_REFETCH_INTERVAL_MS = 5_000;

export function App() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const booksQuery = useQuery({ queryKey: ["books"], queryFn: getBooks });
  const books = booksQuery.data?.books ?? [];

  return (
    <Routes>
      <Route path="/" element={<RootRedirect books={books} loading={booksQuery.isLoading} />} />
      <Route
        path="/books/:bookId/*"
        element={
          <AppShell
            books={books}
            loadingBooks={booksQuery.isLoading}
            mobileNavOpen={mobileNavOpen}
            setMobileNavOpen={setMobileNavOpen}
          />
        }
      />
      <Route path="/setup" element={<SetupShell books={books} mobileNavOpen={mobileNavOpen} setMobileNavOpen={setMobileNavOpen} />} />
    </Routes>
  );
}

function RootRedirect({ books, loading }: { books: BookSummary[]; loading: boolean }) {
  if (loading) {
    return <div className="boot-screen">Buch-Werkbank wird geladen...</div>;
  }
  if (!books.length) {
    return <Navigate to="/setup" replace />;
  }
  return <Navigate to={`/books/${books[0].id}/overview`} replace />;
}

function defaultWorkspaceSettings(book?: BookSummary): WorkspaceSettings {
  const model = book?.ai_model || FALLBACK_OPENROUTER_MODEL;
  return {
    active_style: book?.style_mode ?? "stil-01-original",
    translate_provider: book?.ai_provider ?? "openrouter",
    translate_model: model,
    translate_ollama_model: "gemma4:latest",
    chunk_char_limit: book?.chunk_char_limit ?? 12000,
    review_llm: "none",
    review_llm_scope: "flagged",
    review_model: model,
    review_ollama_model: "gemma4:latest",
    export_format: "docx"
  };
}

function normalizeWorkspaceSettings(settings: Partial<WorkspaceSettings>, defaults: WorkspaceSettings): WorkspaceSettings {
  const normalizeModel = (value: string | undefined) => {
    const model = value || "";
    if (!model || model.toLowerCase().includes("claude")) {
      return defaults.translate_model || FALLBACK_OPENROUTER_MODEL;
    }
    return model;
  };
  return {
    ...defaults,
    ...settings,
    translate_model: normalizeModel(settings.translate_model),
    review_model: normalizeModel(settings.review_model)
  };
}

function settingsStorageKey(bookId?: string): string {
  return `peter-workbench-settings:${bookId ?? "none"}`;
}

function useWorkspaceSettings(book?: BookSummary): [WorkspaceSettings, (next: WorkspaceSettings) => void] {
  const defaults = useMemo(() => defaultWorkspaceSettings(book), [book?.id, book?.style_mode, book?.ai_provider, book?.ai_model, book?.chunk_char_limit]);
  const [settings, setSettingsState] = useState<WorkspaceSettings>(defaults);

  useEffect(() => {
    if (!book) {
      setSettingsState(defaults);
      return;
    }
    try {
      const raw = window.localStorage.getItem(settingsStorageKey(book.id));
      setSettingsState(raw ? normalizeWorkspaceSettings(JSON.parse(raw), defaults) : defaults);
    } catch {
      setSettingsState(defaults);
    }
  }, [book?.id, defaults]);

  const setSettings = (next: WorkspaceSettings) => {
    setSettingsState(next);
    if (book) {
      window.localStorage.setItem(settingsStorageKey(book.id), JSON.stringify(next));
    }
  };

  return [settings, setSettings];
}

function AppShell({
  books,
  loadingBooks,
  mobileNavOpen,
  setMobileNavOpen
}: {
  books: BookSummary[];
  loadingBooks: boolean;
  mobileNavOpen: boolean;
  setMobileNavOpen: (value: boolean) => void;
}) {
  const { bookId = "" } = useParams();
  const navigate = useNavigate();
  const activeBook = books.find((book) => book.id === bookId) ?? books[0];
  const [settings, setSettings] = useWorkspaceSettings(activeBook);

  useEffect(() => {
    if (!loadingBooks && books.length && !books.some((book) => book.id === bookId)) {
      navigate(`/books/${books[0].id}/overview`, { replace: true });
    }
  }, [bookId, books, loadingBooks, navigate]);

  return (
    <div className="app-shell">
      <Sidebar
        books={books}
        activeBook={activeBook}
        mobileOpen={mobileNavOpen}
        onMobileClose={() => setMobileNavOpen(false)}
      />
      <main className="main-area">
        <TopBar activeBook={activeBook} settings={settings} onOpenNav={() => setMobileNavOpen(true)} />
        <Routes>
          <Route path="/" element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<OverviewPage book={activeBook} settings={settings} />} />
          <Route path="translate" element={<TranslatePage book={activeBook} settings={settings} />} />
          <Route path="style-test" element={<StyleTestPage book={activeBook} settings={settings} />} />
          <Route path="review" element={<ReviewPage book={activeBook} settings={settings} />} />
          <Route path="export" element={<ExportPage book={activeBook} settings={settings} />} />
          <Route path="images" element={<ImagesPage book={activeBook} settings={settings} />} />
          <Route path="names" element={<NamesPage book={activeBook} settings={settings} />} />
          <Route path="logs" element={<LogsPage book={activeBook} settings={settings} />} />
          <Route path="settings" element={<SettingsPage book={activeBook} settings={settings} onSettingsChange={setSettings} />} />
        </Routes>
      </main>
    </div>
  );
}

function SetupShell({
  books,
  mobileNavOpen,
  setMobileNavOpen
}: {
  books: BookSummary[];
  mobileNavOpen: boolean;
  setMobileNavOpen: (value: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const [source, setSource] = useState("");
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [style, setStyle] = useState("stil-01-original");
  const [sourceLang, setSourceLang] = useState("ru");
  const [targetLang, setTargetLang] = useState("de");
  const [rulesetApply, setRulesetApply] = useState(false);
  const [activeBookId, setActiveBookId] = useState(books[0]?.id ?? "");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const setupQuery = useQuery({ queryKey: ["setup"], queryFn: getSetup });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: 5_000
  });
  const planMutation = useMutation({ mutationFn: planAction });
  const startMutation = useMutation({
    mutationFn: startActionJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["books"] });
      queryClient.invalidateQueries({ queryKey: ["setup"] });
    }
  });

  const setup = setupQuery.data;
  const sources = setup?.unregistered_sources ?? [];
  const styles = setup?.styles ?? [];
  const selectedSource = sources.find((item) => item.path === source);
  const activeBook = books.find((item) => item.id === activeBookId) ?? books[0];
  const jobs = jobsQuery.data?.jobs ?? [];

  useEffect(() => {
    if (!source && sources[0]) {
      setSource(sources[0].path);
      setTitle(sources[0].title);
      setAuthor(sources[0].author);
    }
  }, [source, sources]);

  useEffect(() => {
    if (selectedSource) {
      setTitle((current) => current || selectedSource.title);
      setAuthor((current) => current || selectedSource.author);
    }
  }, [selectedSource]);

  useEffect(() => {
    if (styles[0] && !styles.some((item) => item.id === style)) {
      setStyle(styles[0].id);
    }
  }, [style, styles]);

  useEffect(() => {
    if (!activeBookId && books[0]) {
      setActiveBookId(books[0].id);
    }
  }, [activeBookId, books]);

  const initPayload: InitBookRequest = {
    action: "init_book",
    source,
    title,
    author,
    style,
    source_lang: sourceLang,
    target_lang: targetLang,
    ruleset_apply: rulesetApply
  };
  const extractPayload: ExtractChaptersRequest | null = activeBook ? { action: "extract_chapters", book_id: activeBook.id } : null;
  const canRegister = Boolean(source && title && style && sourceLang && targetLang);

  return (
    <div className="app-shell">
      <Sidebar books={books} activeBook={activeBook} mobileOpen={mobileNavOpen} onMobileClose={() => setMobileNavOpen(false)} />
      <main className="main-area">
        <TopBar activeBook={activeBook} onOpenNav={() => setMobileNavOpen(true)} />
        <section className="page-stack">
          <PageHeader title="Buch-Setup" description="Neue Buchpakete registrieren und aktuelle Buchquellen vorbereiten." />
          <div className="workflow-grid">
            <div className="panel stack-panel">
              <div className="panel-header">
                <div>
                  <h2>Neue Quelle registrieren</h2>
                  <p>{setupQuery.isLoading ? "Quellen werden gesucht..." : `${sources.length} lose Quelle(n) gefunden`}</p>
                </div>
                <Settings size={22} />
              </div>

              <div className="form-grid">
                <label className="form-field wide">
                  <span>Unregistrierte Quelle</span>
                  <select value={source} onChange={(event) => {
                    const next = sources.find((item) => item.path === event.target.value);
                    setSource(event.target.value);
                    setTitle(next?.title ?? "");
                    setAuthor(next?.author ?? "");
                  }}>
                    {sources.length === 0 && <option value="">Keine losen Quellen gefunden</option>}
                    {sources.map((item) => <option key={item.path} value={item.path}>{item.path}</option>)}
                  </select>
                </label>
                <label className="form-field">
                  <span>Titel</span>
                  <input value={title} onChange={(event) => setTitle(event.target.value)} />
                </label>
                <label className="form-field">
                  <span>Autor</span>
                  <input value={author} onChange={(event) => setAuthor(event.target.value)} />
                </label>
                <label className="form-field">
                  <span>Start-Stil</span>
                  <select value={style} onChange={(event) => setStyle(event.target.value)}>
                    {styles.map((item) => <option key={item.id} value={item.id}>{item.label || item.id}</option>)}
                  </select>
                </label>
                <label className="form-field">
                  <span>Quellsprache</span>
                  <input value={sourceLang} onChange={(event) => setSourceLang(event.target.value)} />
                </label>
                <label className="form-field">
                  <span>Zielsprache</span>
                  <input value={targetLang} onChange={(event) => setTargetLang(event.target.value)} />
                </label>
              </div>

              <div className="toggle-row">
                <label>
                  <input type="checkbox" checked={rulesetApply} onChange={(event) => setRulesetApply(event.target.checked)} />
                  <span>Regelwerk fuer dieses Buch aktivieren</span>
                </label>
              </div>

              {setupQuery.isError && <div className="error-box">{String(setupQuery.error.message)}</div>}
              {planMutation.isError && <div className="error-box">{String(planMutation.error.message)}</div>}
              {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}

              <div className="action-row">
                <button className="button ghost" type="button" disabled={!canRegister || planMutation.isPending} onClick={() => planMutation.mutate(initPayload)}>
                  Kommando planen
                </button>
                <button className="button primary" type="button" disabled={!canRegister || startMutation.isPending} onClick={() => startMutation.mutate(initPayload)}>
                  Buch registrieren
                </button>
              </div>

              {planMutation.data && (
                <div className="command-preview">
                  <span>Geplantes Kommando</span>
                  <pre className="log-tail compact">{planMutation.data.command_text}</pre>
                </div>
              )}

              {setup?.metadata_prompt && (
                <div className="command-preview">
                  <span>Metadaten-Prompt</span>
                  <pre className="style-test-text compact-text raw-text">{setup.metadata_prompt}</pre>
                </div>
              )}
            </div>

            <div className="panel stack-panel">
              <div className="panel-header">
                <div>
                  <h2>Aktuelles Buch vorbereiten</h2>
                  <p>Kapitelquellen aus der registrierten Quelle erzeugen.</p>
                </div>
                <BookOpen size={22} />
              </div>

              <label className="form-field">
                <span>Buch</span>
                <select value={activeBook?.id ?? ""} onChange={(event) => setActiveBookId(event.target.value)}>
                  {books.map((item) => <option key={item.id} value={item.id}>{item.title || item.id}</option>)}
                </select>
              </label>

              {activeBook && (
                <div className="metric-grid">
                  <Metric label="Kapitel" value={activeBook.chapters} />
                  <Metric label="Fehlende Szenen" value={activeBook.missing_scenes} tone={activeBook.missing_scenes ? "warn" : "ok"} />
                  <Metric label="Stil" value={activeBook.style_mode} />
                  <Metric label="Quelle" value={activeBook.source_lang || "-"} />
                </div>
              )}

              <div className="action-row">
                <button className="button ghost" type="button" disabled={!extractPayload || planMutation.isPending} onClick={() => extractPayload && planMutation.mutate(extractPayload)}>
                  Kommando planen
                </button>
                <button className="button primary" type="button" disabled={!extractPayload || startMutation.isPending} onClick={() => extractPayload && startMutation.mutate(extractPayload)}>
                  Quell-Kapitel erzeugen
                </button>
              </div>

              <JobPanel
                jobs={jobs}
                loading={jobsQuery.isLoading}
                selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
                onSelectJob={setSelectedJobId}
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function Sidebar({
  books,
  activeBook,
  mobileOpen,
  onMobileClose
}: {
  books: BookSummary[];
  activeBook?: BookSummary;
  mobileOpen: boolean;
  onMobileClose: () => void;
}) {
  const navigate = useNavigate();

  return (
    <>
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="sidebar-head">
          <div>
            <div className="brand">Buch-Werkbank</div>
            <div className="brand-subtitle">FastAPI + React</div>
          </div>
          <button className="icon-button mobile-only" type="button" onClick={onMobileClose} aria-label="Navigation schliessen">
            <X size={18} />
          </button>
        </div>

        <label className="field-label" htmlFor="book-select">Buch</label>
        <select
          id="book-select"
          className="book-select"
          value={activeBook?.id ?? ""}
          onChange={(event) => {
            if (event.target.value) {
              navigate(`/books/${event.target.value}/overview`);
              onMobileClose();
            }
          }}
        >
          {books.map((book) => (
            <option key={book.id} value={book.id}>{book.title || book.id}</option>
          ))}
        </select>

        <nav className="nav-list" aria-label="Hauptnavigation">
          {activeBook && navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={`/books/${activeBook.id}/${item.path}`}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                onClick={onMobileClose}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          <NavLink to="/setup" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`} onClick={onMobileClose}>
            <Settings size={18} />
            <span>Buch-Setup</span>
          </NavLink>
        </nav>

        <div className="sidebar-note">
          <Activity size={16} />
          <span>React/FastAPI ist das primaere Dashboard. Streamlit bleibt Legacy.</span>
        </div>
      </aside>
      {mobileOpen && <button className="nav-backdrop mobile-only" type="button" aria-label="Navigation schliessen" onClick={onMobileClose} />}
    </>
  );
}

function TopBar({ activeBook, settings, onOpenNav }: { activeBook?: BookSummary; settings?: WorkspaceSettings; onOpenNav: () => void }) {
  return (
    <header className="top-bar">
      <button className="icon-button mobile-only" type="button" onClick={onOpenNav} aria-label="Navigation oeffnen">
        <Menu size={20} />
      </button>
      <div className="top-title">
        <span>{activeBook?.title ?? "Buch-Werkbank"}</span>
        <small>
          {activeBook ? `${activeBook.source_lang?.toUpperCase() ?? "RU"} -> ${activeBook.target_lang?.toUpperCase() ?? "DE"} / ${settings?.active_style ?? activeBook.style_mode}` : "Kein Buch geladen"}
        </small>
      </div>
      <div className="top-status">React/FastAPI</div>
    </header>
  );
}

function OverviewPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, settings.active_style],
    queryFn: () => getChapters(book!.id, settings.active_style),
    enabled: Boolean(book)
  });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: 3_000
  });

  const jobs = jobsQuery.data?.jobs ?? [];
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : jobs[0];
  const chapters = chaptersQuery.data?.chapters ?? [];
  const totals = useMemo(() => summarizeChapters(chapters), [chapters]);

  useEffect(() => {
    if (!selectedJobId && jobs[0]) {
      setSelectedJobId(jobs[0].job_id);
    }
  }, [jobs, selectedJobId]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  return (
    <section className="page-stack">
      <PageHeader
        title="Uebersicht"
        description="Buchstatus, Kapitelabdeckung und Hintergrundjobs aus der neuen FastAPI-Schicht."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="overview-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Buchstatus</h2>
              <p>{book.author || "Autor nicht gesetzt"}</p>
            </div>
            <BookOpen size={22} />
          </div>
          <div className="metric-grid">
            <Metric label="Kapitel" value={book.chapters} />
            <Metric label="Quellszenen" value={totals.source} />
            <Metric label="DE-Szenen" value={totals.de} />
            <Metric label="Fehlend" value={totals.missing} tone={totals.missing ? "warn" : "ok"} />
          </div>
          <ChapterTable chapters={chapters} loading={chaptersQuery.isLoading} />
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJob?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function PageHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </div>
  );
}

function ContextBar({ book, settings, selectedJob }: { book: BookSummary; settings?: WorkspaceSettings; selectedJob?: JobDetail }) {
  return (
    <div className="context-bar">
      <span>Buch: {book.id}</span>
      <span>Stil: {settings?.active_style ?? book.style_mode}</span>
      {settings?.translate_provider && <span>Provider: {settings.translate_provider}</span>}
      {settings?.translate_model && <span>Modell: {settings.translate_model}</span>}
      <span>Kapitel: {book.chapters}</span>
      <span>Job: {selectedJob ? `${selectedJob.kind ?? "job"} / ${selectedJob.status}` : "keiner"}</span>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: number | string; tone?: "ok" | "warn" }) {
  return (
    <div className={`metric ${tone ?? ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ChapterTable({ chapters, loading }: { chapters: ChapterRow[]; loading: boolean }) {
  if (loading) {
    return <div className="table-state">Kapitel werden geladen...</div>;
  }
  if (!chapters.length) {
    return <div className="table-state">Noch keine Kapitelstatusdaten vorhanden.</div>;
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Kapitel</th>
            <th>Status</th>
            <th>Quelle</th>
            <th>DE</th>
            <th>Fehlt</th>
            <th>Naechste</th>
          </tr>
        </thead>
        <tbody>
          {chapters.slice(0, 12).map((chapter) => (
            <tr key={chapter.Kapitel}>
              <td>{chapter.Kapitel}</td>
              <td>{chapter.Status || "-"}</td>
              <td>{chapter.RU}</td>
              <td>{chapter.DE}</td>
              <td className={chapter.Fehlt ? "text-warn" : "text-ok"}>{chapter.Fehlt}</td>
              <td>{chapter["Naechste Szene"] || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobPanel({
  jobs,
  loading,
  selectedJobId,
  onSelectJob
}: {
  jobs: JobDetail[];
  loading: boolean;
  selectedJobId: string | null;
  onSelectJob: (jobId: string) => void;
}) {
  const queryClient = useQueryClient();
  const [liveJob, setLiveJob] = useState<JobDetail | null>(null);
  const selectedJobQuery = useQuery({
    queryKey: ["job", selectedJobId],
    queryFn: () => getJob(selectedJobId!),
    enabled: Boolean(selectedJobId)
  });
  const stopMutation = useMutation({
    mutationFn: stopJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["job", selectedJobId] });
    }
  });

  useEffect(() => {
    if (!selectedJobId) {
      setLiveJob(null);
      return;
    }
    let closed = false;
    let source: EventSource | null = null;
    let reconnectTimer: number | null = null;

    const connect = () => {
      source = new EventSource(jobEventsUrl(selectedJobId));
      source.addEventListener("job", (event) => {
        setLiveJob(parseSseJobPayload((event as MessageEvent).data));
      });
      source.onerror = () => {
        source?.close();
        source = null;
        if (!closed) {
          reconnectTimer = window.setTimeout(connect, 1500);
        }
      };
    };

    connect();
    return () => {
      closed = true;
      source?.close();
      if (reconnectTimer !== null) {
        window.clearTimeout(reconnectTimer);
      }
    };
  }, [selectedJobId]);

  const selectedJob = liveJob ?? selectedJobQuery.data?.job ?? jobs.find((job) => job.job_id === selectedJobId) ?? null;
  const runningCount = jobs.filter((job) => job.running).length;
  const jobSummary = loading
    ? "Jobs werden geladen..."
    : runningCount
      ? `${runningCount} laufen, ${jobs.length} letzte Jobs`
      : `${jobs.length} letzte Jobs`;

  return (
    <aside className="panel job-panel">
      <div className="panel-header">
        <div>
          <h2>Hintergrundjobs</h2>
          <p>{jobSummary}</p>
        </div>
        <RefreshCw size={21} />
      </div>
      <div className="job-list">
        {jobs.length === 0 && <div className="table-state">Noch keine Jobs vorhanden.</div>}
        {jobs.map((job) => (
          <button
            key={job.job_id}
            type="button"
            className={`job-row ${job.job_id === selectedJobId ? "selected" : ""}`}
            onClick={() => onSelectJob(job.job_id)}
            title={job.job_id}
          >
            <span className={`status-dot ${job.running ? "running" : job.status}`} />
            <span>
              <strong>{job.kind || "job"}</strong>
              <small>{job.book_id || "-"} / {job.style || "-"}</small>
            </span>
            <em>{job.status}</em>
          </button>
        ))}
      </div>
      <div className="job-detail">
        {selectedJob ? (
          <>
            <div className="job-detail-head">
              <div>
                <h3>{selectedJob.kind || "Job"}: {selectedJob.status}</h3>
                <p title={selectedJob.job_id}>{selectedJob.job_id}</p>
              </div>
              <button
                className="button secondary"
                type="button"
                disabled={!selectedJob.running || stopMutation.isPending}
                onClick={() => stopMutation.mutate(selectedJob.job_id)}
              >
                <Square size={16} />
                Stop
              </button>
            </div>
            <div className="progress-line">
              <span>Fortschritt</span>
              <strong>{formatProgress(selectedJob)}</strong>
            </div>
            <IssueBadges job={selectedJob} />
            {selectedJob.log_path && (
              <div className="action-row">
                <a className="button secondary link-button" href={`/books/${selectedJob.book_id || ""}/logs?log=${encodeURIComponent(encodeLogPath(selectedJob.log_path))}`}>
                  <ScrollText size={16} />
                  Log oeffnen
                </a>
                <code>{selectedJob.log_path}</code>
              </div>
            )}
            <LogContent text={selectedJob.log_tail || "(noch kein Log-Tail)"} />
          </>
        ) : (
          <div className="empty-state compact">
            <PauseCircle size={24} />
            <span>Kein Job ausgewaehlt.</span>
          </div>
        )}
      </div>
    </aside>
  );
}

function IssueBadges({ job }: { job: JobDetail }) {
  const issues = classifyJobIssues(job);
  if (!issues.length) {
    return null;
  }
  return (
    <div className="badge-row">
      {issues.map((issue) => (
        <span key={issue} className="issue-badge">{issue}</span>
      ))}
    </div>
  );
}

function classifyJobIssues(job: JobDetail): string[] {
  const text = `${job.status} ${job.provider ?? ""} ${job.log_tail ?? ""}`.toLowerCase();
  const issues = new Set<string>();
  if (text.includes("prompt-echo") || text.includes("modellantwort wirkt wie prompt-echo")) {
    issues.add("Prompt-Echo");
  }
  if (text.includes("llm_review_failed") || text.includes("kein json-objekt") || text.includes("ki-review fehlgeschlagen")) {
    issues.add("LLM-Antwort");
  }
  if (text.includes("ollama") && (text.includes("connection refused") || text.includes("verbindung") || text.includes("failed"))) {
    issues.add("Ollama");
  }
  if (text.includes("openrouter") && (text.includes("error") || text.includes("failed") || text.includes("rate limit"))) {
    issues.add("OpenRouter");
  }
  if (text.includes("fehler") || text.includes("error") || job.status === "failed") {
    issues.add("Fehler");
  }
  if (text.includes("warning") || text.includes("warnung")) {
    issues.add("Warnung");
  }
  return [...issues];
}

function encodeLogPath(path: string): string {
  const bytes = new TextEncoder().encode(path.replace(/\\/g, "/"));
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function TranslatePage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [style, setStyle] = useState(settings.active_style);
  const [scope, setScope] = useState("Aktuelles Kapitel");
  const [chapter, setChapter] = useState("");
  const [scene, setScene] = useState("01");
  const [startChapter, setStartChapter] = useState("");
  const [endChapter, setEndChapter] = useState("");
  const [provider, setProvider] = useState(settings.translate_provider);
  const [model, setModel] = useState(settings.translate_model);
  const [ollamaModel, setOllamaModel] = useState(settings.translate_ollama_model);
  const [chunkCharLimit, setChunkCharLimit] = useState(settings.chunk_char_limit);
  const [overwrite, setOverwrite] = useState(false);
  const [assembleAfter, setAssembleAfter] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [lastPlanMode, setLastPlanMode] = useState<"run" | "dry-run" | null>(null);

  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, style || book?.style_mode],
    queryFn: () => getChapters(book!.id, style || book!.style_mode),
    enabled: Boolean(book)
  });
  const stylesQuery = useQuery({
    queryKey: ["styles", book?.id],
    queryFn: () => getBookStyles(book!.id),
    enabled: Boolean(book)
  });
  const modelsQuery = useQuery({ queryKey: ["models"], queryFn: getModels });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: JOBS_REFETCH_INTERVAL_MS
  });
  const startMutation = useMutation({
    mutationFn: startTranslateBatchJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["chapters", book?.id] });
    }
  });
  const planMutation = useMutation({
    mutationFn: planAction
  });

  const chapters = chaptersQuery.data?.chapters ?? [];
  const jobs = jobsQuery.data?.jobs ?? [];
  const styleOptions = stylesQuery.data?.styles ?? [];
  const models = modelsQuery.data?.models ?? [];
  const openRouterModels = models.filter((item) => item.id);
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : undefined;
  const stylesLoadError = stylesQuery.isError ? String(stylesQuery.error.message) : "";
  const modelsLoadError = modelsQuery.isError ? String(modelsQuery.error.message) : "";

  useEffect(() => {
    setStyle(settings.active_style);
    setProvider(settings.translate_provider);
    setModel(settings.translate_model);
    setOllamaModel(settings.translate_ollama_model);
    setChunkCharLimit(settings.chunk_char_limit);
  }, [book?.id, settings]);

  useEffect(() => {
    const firstChapter = chapters[0]?.Kapitel;
    if (firstChapter && !chapter) {
      setChapter(firstChapter);
      setStartChapter(firstChapter);
      setEndChapter(firstChapter);
    }
  }, [chapter, chapters]);

  useEffect(() => {
    if (!model && openRouterModels[0]) {
      setModel(openRouterModels[0].id);
    }
  }, [model, openRouterModels]);

  useEffect(() => {
    if (!selectedJob || selectedJob.running) {
      return;
    }
    if (["completed", "failed", "stopped", "stale"].includes(selectedJob.status)) {
      queryClient.invalidateQueries({ queryKey: ["style-test", book?.id, chapter] });
      queryClient.invalidateQueries({ queryKey: ["chapters", book?.id] });
    }
  }, [book?.id, chapter, queryClient, selectedJob?.job_id, selectedJob?.running, selectedJob?.status]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  const canStart = Boolean(
    style &&
    provider &&
    (scope !== "Aktuelles Kapitel" || chapter) &&
    (scope !== "Einzelne Szene" || (chapter && scene)) &&
    (scope !== "Bereich" || (startChapter && endChapter))
  );
  const payload = buildTranslatePayload({
    bookId: book.id,
    style,
    provider,
    scope,
    chapter,
    scene,
    startChapter,
    endChapter,
    model,
    ollamaModel,
    chunkCharLimit,
    overwrite,
    assembleAfter
  });
  const planPayload = (dryRun: boolean) => ({ ...payload, dry_run: dryRun });

  return (
    <section className="page-stack">
      <PageHeader
        title="Uebersetzen"
        description="Erster React-Slice fuer Uebersetzungsjobs: sichtbarer Kontext, echte FastAPI-Aktion, Fortschritt im globalen Job-Panel."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Job konfigurieren</h2>
              <p>Startet `translate_batch.py` als Hintergrundjob.</p>
            </div>
            <Languages size={22} />
          </div>

          <div className="form-grid">
            <label className="form-field">
              <span>Stil</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styleOptions.length === 0 && <option value={style}>{style || "Keine Styles geladen"}</option>}
                {styleOptions.map((item) => (
                  <option key={item.id} value={item.id}>{item.label || item.id}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Scope</span>
              <select value={scope} onChange={(event) => setScope(event.target.value)}>
                <option>Aktuelles Kapitel</option>
                <option>Einzelne Szene</option>
                <option>Bereich</option>
                <option>Fehlende</option>
              </select>
            </label>

            {(scope === "Aktuelles Kapitel" || scope === "Einzelne Szene") && (
              <label className="form-field">
                <span>Kapitel</span>
                <select value={chapter} onChange={(event) => setChapter(event.target.value)}>
                  {chapters.map((item) => (
                    <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel} / fehlt {item.Fehlt}</option>
                  ))}
                </select>
              </label>
            )}

            {scope === "Einzelne Szene" && (
              <label className="form-field">
                <span>Szene</span>
                <input value={scene} onChange={(event) => setScene(event.target.value)} placeholder="01" />
              </label>
            )}

            {scope === "Bereich" && (
              <>
                <label className="form-field">
                  <span>Von</span>
                  <select value={startChapter} onChange={(event) => setStartChapter(event.target.value)}>
                    {chapters.map((item) => <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>)}
                  </select>
                </label>
                <label className="form-field">
                  <span>Bis</span>
                  <select value={endChapter} onChange={(event) => setEndChapter(event.target.value)}>
                    {chapters.map((item) => <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>)}
                  </select>
                </label>
              </>
            )}

            <label className="form-field">
              <span>Provider</span>
              <select value={provider} onChange={(event) => setProvider(event.target.value)}>
                <option value="openrouter">OpenRouter</option>
                <option value="ollama">Ollama</option>
                <option value="prompt_file">Prompt-Datei</option>
                <option value="workspace_ai">Workspace-KI</option>
              </select>
            </label>

            {provider === "openrouter" && (
              <label className="form-field wide">
                <span>Modell</span>
                <select value={model} onChange={(event) => setModel(event.target.value)}>
                  {openRouterModels.length === 0 && <option value="">Keine Modelle geladen</option>}
                  {openRouterModels.map((item) => (
                    <option key={item.id} value={item.id}>{item.name ? `${item.name} (${item.provider})` : item.id}</option>
                  ))}
                </select>
              </label>
            )}

            {provider === "ollama" && (
              <label className="form-field">
                <span>Ollama-Modell</span>
                <input value={ollamaModel} onChange={(event) => setOllamaModel(event.target.value)} placeholder="gemma4:latest" />
              </label>
            )}

            <label className="form-field">
              <span>Chunk-Grenze</span>
              <input
                type="number"
                min="1000"
                step="500"
                value={chunkCharLimit}
                onChange={(event) => setChunkCharLimit(Number(event.target.value))}
              />
            </label>
          </div>

          {(stylesLoadError || modelsLoadError) && (
            <div className="error-box">
              API-Daten fehlen. Backend bitte neu starten. {stylesLoadError || modelsLoadError}
            </div>
          )}

          <div className="toggle-row">
            <label>
              <input type="checkbox" checked={assembleAfter} onChange={(event) => setAssembleAfter(event.target.checked)} />
              <span>Nach erfolgreichem Lauf Kapitel zusammensetzen</span>
            </label>
            <label>
              <input type="checkbox" checked={overwrite} onChange={(event) => setOverwrite(event.target.checked)} />
              <span>Bestehende Szenen ersetzen</span>
            </label>
          </div>

          {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}
          {planMutation.isError && <div className="error-box">{String(planMutation.error.message)}</div>}

          <div className="action-row">
            <button className="button primary" type="button" disabled={!canStart || startMutation.isPending} onClick={() => startMutation.mutate(payload)}>
              <Languages size={16} />
              Job starten
            </button>
            <button
              className="button secondary"
              type="button"
              disabled={!canStart || planMutation.isPending}
              onClick={() => {
                setLastPlanMode("run");
                planMutation.mutate(planPayload(false));
              }}
            >
              <FileText size={16} />
              Kommando anzeigen
            </button>
            <button
              className="button secondary"
              type="button"
              disabled={!canStart || planMutation.isPending}
              onClick={() => {
                setLastPlanMode("dry-run");
                planMutation.mutate(planPayload(true));
              }}
            >
              <ListChecks size={16} />
              Dry-run anzeigen
            </button>
            <code>{payload.scope}{payload.chapter ? ` / ${payload.chapter}` : ""}</code>
          </div>

          {planMutation.data && (
            <div className="command-preview">
              <div className="progress-line">
                <span>{lastPlanMode === "dry-run" ? "Dry-run-Kommando" : "Start-Kommando"}</span>
                <strong>{planMutation.data.action}</strong>
              </div>
              <pre className="log-tail compact">{planMutation.data.command_text}</pre>
            </div>
          )}
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function buildTranslatePayload(options: {
  bookId: string;
  style: string;
  provider: string;
  scope: string;
  chapter: string;
  scene: string;
  startChapter: string;
  endChapter: string;
  model: string;
  ollamaModel: string;
  chunkCharLimit: number;
  overwrite: boolean;
  assembleAfter: boolean;
}): TranslateBatchRequest {
  const payload: TranslateBatchRequest = {
    action: options.scope === "Einzelne Szene" ? "translate_chapter" : "translate_batch",
    book_id: options.bookId,
    style: options.style,
    provider: options.provider,
    scope: options.scope,
    chunk_char_limit: options.chunkCharLimit || undefined,
    overwrite: options.overwrite,
    auto_status: true,
    assemble_after: options.assembleAfter
  };
  if (options.scope === "Aktuelles Kapitel" || options.scope === "Einzelne Szene") {
    payload.chapter = options.chapter;
  }
  if (options.scope === "Einzelne Szene") {
    payload.scene = options.scene;
  }
  if (options.scope === "Bereich") {
    payload.start_chapter = options.startChapter;
    payload.end_chapter = options.endChapter;
  }
  if (options.provider === "openrouter") {
    payload.model = options.model;
  }
  if (options.provider === "ollama") {
    payload.ollama_model = options.ollamaModel;
  }
  return payload;
}

function StyleTestPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [chapter, setChapter] = useState("");
  const [scene, setScene] = useState("");
  const [provider, setProvider] = useState(settings.translate_provider);
  const [model, setModel] = useState(settings.translate_model);
  const [ollamaModel, setOllamaModel] = useState(settings.translate_ollama_model);
  const [overwrite, setOverwrite] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, settings.active_style],
    queryFn: () => getChapters(book!.id, settings.active_style || book!.style_mode),
    enabled: Boolean(book)
  });
  const modelsQuery = useQuery({ queryKey: ["models"], queryFn: getModels });
  const styleTestQuery = useQuery({
    queryKey: ["style-test", book?.id, chapter, scene],
    queryFn: () => getStyleTest(book!.id, chapter, scene),
    enabled: Boolean(book && chapter)
  });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: JOBS_REFETCH_INTERVAL_MS
  });
  const startMutation = useMutation({
    mutationFn: startTranslateBatchJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["style-test", book?.id, chapter] });
    }
  });
  const chapters = chaptersQuery.data?.chapters ?? [];
  const openRouterModels = (modelsQuery.data?.models ?? []).filter((item) => item.id);
  const styleTest = styleTestQuery.data;
  const jobs = jobsQuery.data?.jobs ?? [];
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : undefined;

  useEffect(() => {
    setProvider(settings.translate_provider);
    setModel(settings.translate_model);
    setOllamaModel(settings.translate_ollama_model);
  }, [book?.id, settings]);

  useEffect(() => {
    const firstChapter = chapters[0]?.Kapitel;
    if (firstChapter && !chapter) {
      setChapter(firstChapter);
    }
  }, [chapter, chapters]);

  useEffect(() => {
    const firstScene = styleTest?.selected_scene || styleTest?.scenes[0] || "";
    if (firstScene && !scene) {
      setScene(firstScene);
    }
  }, [scene, styleTest]);

  useEffect(() => {
    if (!model && openRouterModels[0]) {
      setModel(openRouterModels[0].id);
    }
  }, [model, openRouterModels]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  const buildPayloadForStyle = (style: string): TranslateBatchRequest => ({
    action: "translate_chapter",
    book_id: book.id,
    style,
    provider,
    scope: "Einzelne Szene",
    chapter,
    scene: styleTest?.selected_scene || scene,
    model: provider === "openrouter" ? model : undefined,
    ollama_model: provider === "ollama" ? ollamaModel : undefined,
    chunk_char_limit: settings.chunk_char_limit || undefined,
    overwrite
  });
  const canRun = Boolean(chapter && (styleTest?.selected_scene || scene) && provider);
  const originalChars = countCharacters(styleTest?.source?.content || "");

  return (
    <section className="page-stack">
      <PageHeader
        title="Stiltest"
        description="Originalszene und Style-Ergebnisse nebeneinander vergleichen; einzelne Szenen pro Stil neu erzeugen."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="panel stack-panel">
        <div className="panel-header">
          <div>
            <h2>Vergleich</h2>
            <p>{styleTest?.selected_scene ? `Kapitel ${chapter}, Szene ${styleTest.selected_scene}` : "Keine Quell-Szene geladen"}</p>
          </div>
        </div>
        <div className="compare-grid style-test-grid">
          <StyleCompareCard
            title={`Original ${(styleTest?.source_lang || book.source_lang || "ru").toUpperCase()}`}
            path={styleTest?.source?.path?.path}
            content={styleTest?.source?.content || ""}
            baseChars={originalChars}
            isOriginal
          />
          {(styleTest?.styles ?? []).map((item) => {
            const payload = buildPayloadForStyle(item.id);
            const content = item.scene.content || item.prompt.content;
            const label = item.scene.content ? "Uebersetzung" : item.prompt.content ? "Prompt" : "Noch kein Ergebnis";
            return (
              <StyleCompareCard
                key={item.id}
                title={item.label || item.id}
                subtitle={label}
                path={item.scene.path?.path || item.prompt.path?.path}
                content={content}
                baseChars={originalChars}
                actions={(
                  <>
                    <button className="button primary" type="button" disabled={!canRun || startMutation.isPending} onClick={() => startMutation.mutate(payload)}>
                      Erzeugen
                    </button>
                  </>
                )}
              />
            );
          })}
        </div>
      </div>
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Test konfigurieren</h2>
              <p>Erzeugt bei Start `translate_chapter.py` fuer genau eine Szene und einen Stil.</p>
            </div>
            <Activity size={22} />
          </div>

          <div className="form-grid">
            <label className="form-field">
              <span>Kapitel</span>
              <select value={chapter} onChange={(event) => { setChapter(event.target.value); setScene(""); }}>
                {chapters.map((item) => (
                  <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel} / RU {item.RU} / DE {item.DE}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Szene</span>
              <select value={styleTest?.selected_scene || scene} onChange={(event) => setScene(event.target.value)}>
                {(styleTest?.scenes ?? []).map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Provider</span>
              <select value={provider} onChange={(event) => setProvider(event.target.value)}>
                <option value="prompt_file">Prompt-Datei</option>
                <option value="openrouter">OpenRouter</option>
                <option value="ollama">Ollama</option>
                <option value="workspace_ai">Workspace-KI</option>
              </select>
            </label>

            {provider === "openrouter" && (
              <label className="form-field wide">
                <span>Modell</span>
                <select value={model} onChange={(event) => setModel(event.target.value)}>
                  {openRouterModels.length === 0 && <option value="">Keine Modelle geladen</option>}
                  {openRouterModels.map((item) => (
                    <option key={item.id} value={item.id}>{item.name ? `${item.name} (${item.provider})` : item.id}</option>
                  ))}
                </select>
              </label>
            )}

            {provider === "ollama" && (
              <label className="form-field">
                <span>Ollama-Modell</span>
                <input value={ollamaModel} onChange={(event) => setOllamaModel(event.target.value)} placeholder="gemma4:latest" />
              </label>
            )}
          </div>

          <div className="toggle-row">
            <label>
              <input type="checkbox" checked={overwrite} onChange={(event) => setOverwrite(event.target.checked)} />
              <span>Vorhandenes Ergebnis ersetzen</span>
            </label>
          </div>

          {styleTestQuery.isError && <div className="error-box">{String(styleTestQuery.error.message)}</div>}
          {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function StyleCompareCard({
  title,
  subtitle,
  path,
  content,
  baseChars,
  isOriginal = false,
  actions
}: {
  title: string;
  subtitle?: string;
  path?: string;
  content: string;
  baseChars?: number;
  isOriginal?: boolean;
  actions?: ReactNode;
}) {
  const chars = countCharacters(content);
  const ratio = baseChars && chars ? Math.round((chars / baseChars) * 100) : 0;
  return (
    <div className="compare-card">
      <div className="compare-card-header">
        <div>
          <h3>{title}</h3>
          {subtitle && <span>{subtitle}</span>}
          <div className="compare-metrics">
            <strong>{formatNumber(chars)}</strong>
            <span>Zeichen</span>
            {!isOriginal && baseChars ? <em>{ratio}% vom Original</em> : <em>Originalbasis</em>}
          </div>
        </div>
        {actions && <div className="compare-actions">{actions}</div>}
      </div>
      {path && <code>{path}</code>}
      <StyleTestText content={content} />
    </div>
  );
}

function StyleTestText({ content }: { content: string }) {
  if (!content) {
    return <div className="style-test-text">(leer)</div>;
  }
  return (
    <div className="style-test-text">
      {content.split("\n").map((rawLine, index) => {
        const line = rawLine.replace(/\s+$/, "");
        const trimmed = line.trim();
        const isQuote = trimmed.startsWith(">");
        const quoteText = isQuote ? trimmed.replace(/^>\s?/, "") : line;
        const isAside = !isQuote && isAsideLine(trimmed);
        const className = [
          "style-test-line",
          !trimmed ? "blank" : "",
          isQuote ? "quote" : "",
          isAside ? "aside" : ""
        ].filter(Boolean).join(" ");
        return (
          <div key={`${index}-${rawLine.slice(0, 18)}`} className={className}>
            {trimmed ? renderInlineMarkdown(quoteText) : "\u00a0"}
          </div>
        );
      })}
    </div>
  );
}

function isAsideLine(value: string): boolean {
  if (value.length < 8) {
    return false;
  }
  return (
    (value.startsWith("(") && value.endsWith(")")) ||
    (value.startsWith("[") && value.endsWith("]"))
  );
}

function renderInlineMarkdown(value: string): ReactNode[] {
  const parts = value.split(/(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_)/g).filter((part) => part !== "");
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if ((part.startsWith("*") && part.endsWith("*")) || (part.startsWith("_") && part.endsWith("_"))) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    return <span key={index}>{part}</span>;
  });
}

function countCharacters(value: string): number {
  return Array.from((value || "").trim()).length;
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("de-DE").format(value);
}

function reviewSummaryCounts(summary?: Record<string, unknown> | null): { ERROR: number; WARNING: number; INFO: number } {
  const counts = (summary?.counts ?? {}) as Record<string, unknown>;
  return {
    ERROR: Number(counts.ERROR ?? 0),
    WARNING: Number(counts.WARNING ?? 0),
    INFO: Number(counts.INFO ?? 0)
  };
}

function ReviewPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [style, setStyle] = useState(settings.active_style);
  const [scope, setScope] = useState("Aktuelles Kapitel");
  const [chapter, setChapter] = useState("");
  const [startChapter, setStartChapter] = useState("");
  const [endChapter, setEndChapter] = useState("");
  const [llm, setLlm] = useState(settings.review_llm);
  const [llmScope, setLlmScope] = useState(settings.review_llm_scope);
  const [model, setModel] = useState(settings.review_model);
  const [ollamaModel, setOllamaModel] = useState(settings.review_ollama_model);
  const [failOnErrors, setFailOnErrors] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, style || book?.style_mode],
    queryFn: () => getChapters(book!.id, style || book!.style_mode),
    enabled: Boolean(book)
  });
  const stylesQuery = useQuery({
    queryKey: ["styles", book?.id],
    queryFn: () => getBookStyles(book!.id),
    enabled: Boolean(book)
  });
  const modelsQuery = useQuery({ queryKey: ["models"], queryFn: getModels });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: JOBS_REFETCH_INTERVAL_MS
  });
  const reviewQuery = useQuery({
    queryKey: ["review", book?.id, style],
    queryFn: () => getReviewArtifacts(book!.id, style),
    enabled: Boolean(book && style)
  });
  const startMutation = useMutation({
    mutationFn: startReviewJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });
  const fixMutation = useMutation({
    mutationFn: startReviewFixJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["review", book?.id, style] });
    }
  });
  const planMutation = useMutation({ mutationFn: planAction });

  const chapters = chaptersQuery.data?.chapters ?? [];
  const jobs = jobsQuery.data?.jobs ?? [];
  const styleOptions = stylesQuery.data?.styles ?? [];
  const openRouterModels = (modelsQuery.data?.models ?? []).filter((item) => item.id);
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : undefined;
  const review = reviewQuery.data;
  const selectedReport = review?.reports[0];
  const stylesLoadError = stylesQuery.isError ? String(stylesQuery.error.message) : "";
  const modelsLoadError = modelsQuery.isError ? String(modelsQuery.error.message) : "";

  useEffect(() => {
    setStyle(settings.active_style);
    setLlm(settings.review_llm);
    setLlmScope(settings.review_llm_scope);
    setModel(settings.review_model);
    setOllamaModel(settings.review_ollama_model);
  }, [book?.id, settings]);

  useEffect(() => {
    const firstChapter = chapters[0]?.Kapitel;
    if (firstChapter && !chapter) {
      setChapter(firstChapter);
      setStartChapter(firstChapter);
      setEndChapter(firstChapter);
    }
  }, [chapter, chapters]);

  useEffect(() => {
    if (!model && openRouterModels[0]) {
      setModel(openRouterModels[0].id);
    }
  }, [model, openRouterModels]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  const canStart = Boolean(style && llm && llmScope && (scope !== "Aktuelles Kapitel" || chapter) && (scope !== "Bereich" || (startChapter && endChapter)));
  const payload = buildReviewPayload({
    bookId: book.id,
    style,
    scope,
    chapter,
    startChapter,
    endChapter,
    llm,
    llmScope,
    model,
    ollamaModel,
    failOnErrors
  });
  const fixPayload = (fixAction: "plan" | "stage" | "promote"): ReviewFixRequest => ({
    action: "review_fixes",
    book_id: book.id,
    style,
    fix_action: fixAction
  });
  const summaryCounts = reviewSummaryCounts(review?.summary);

  return (
    <section className="page-stack">
      <PageHeader
        title="Review"
        description="Review-Laeufe aus React starten: Regelcheck, optionaler LLM-Review und Fortschritt im globalen Job-Panel."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Review konfigurieren</h2>
              <p>Startet `review_manuscript.py` als Hintergrundjob.</p>
            </div>
            <ListChecks size={22} />
          </div>

          <div className="form-grid">
            <label className="form-field">
              <span>Stil</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styleOptions.length === 0 && <option value={style}>{style || "Keine Styles geladen"}</option>}
                {styleOptions.map((item) => (
                  <option key={item.id} value={item.id}>{item.label || item.id}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Scope</span>
              <select value={scope} onChange={(event) => setScope(event.target.value)}>
                <option>Aktuelles Kapitel</option>
                <option>Bereich</option>
                <option>Alle</option>
              </select>
            </label>

            {scope === "Aktuelles Kapitel" && (
              <label className="form-field">
                <span>Kapitel</span>
                <select value={chapter} onChange={(event) => setChapter(event.target.value)}>
                  {chapters.map((item) => (
                    <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel} / DE {item.DE}</option>
                  ))}
                </select>
              </label>
            )}

            {scope === "Bereich" && (
              <>
                <label className="form-field">
                  <span>Von</span>
                  <select value={startChapter} onChange={(event) => setStartChapter(event.target.value)}>
                    {chapters.map((item) => <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>)}
                  </select>
                </label>
                <label className="form-field">
                  <span>Bis</span>
                  <select value={endChapter} onChange={(event) => setEndChapter(event.target.value)}>
                    {chapters.map((item) => <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>)}
                  </select>
                </label>
              </>
            )}

            <label className="form-field">
              <span>LLM</span>
              <select value={llm} onChange={(event) => setLlm(event.target.value)}>
                <option value="none">Nur Regelcheck</option>
                <option value="openrouter">OpenRouter</option>
                <option value="ollama">Ollama</option>
              </select>
            </label>

            <label className="form-field">
              <span>LLM-Scope</span>
              <select value={llmScope} onChange={(event) => setLlmScope(event.target.value)}>
                <option value="flagged">Nur markierte Szenen</option>
                <option value="all">Alle Szenen</option>
              </select>
            </label>

            {llm === "openrouter" && (
              <label className="form-field wide">
                <span>Modell</span>
                <select value={model} onChange={(event) => setModel(event.target.value)}>
                  {openRouterModels.length === 0 && <option value="">Keine Modelle geladen</option>}
                  {openRouterModels.map((item) => (
                    <option key={item.id} value={item.id}>{item.name ? `${item.name} (${item.provider})` : item.id}</option>
                  ))}
                </select>
              </label>
            )}

            {llm === "ollama" && (
              <label className="form-field">
                <span>Ollama-Modell</span>
                <input value={ollamaModel} onChange={(event) => setOllamaModel(event.target.value)} placeholder="gemma4:latest" />
              </label>
            )}
          </div>

          {(stylesLoadError || modelsLoadError) && (
            <div className="error-box">
              API-Daten fehlen. Backend bitte neu starten. {stylesLoadError || modelsLoadError}
            </div>
          )}

          <div className="toggle-row">
            <label>
              <input type="checkbox" checked={failOnErrors} onChange={(event) => setFailOnErrors(event.target.checked)} />
              <span>Bei Review-Fehlern Job als fehlgeschlagen behandeln</span>
            </label>
          </div>

          {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}

          <div className="action-row">
            <button className="button primary" type="button" disabled={!canStart || startMutation.isPending} onClick={() => startMutation.mutate(payload)}>
              <ListChecks size={16} />
              Review starten
            </button>
            <button className="button ghost" type="button" disabled={!canStart || planMutation.isPending} onClick={() => planMutation.mutate(payload)}>
              Kommando planen
            </button>
            <code>{payload.scope}{payload.chapter ? ` / ${payload.chapter}` : ""} / {payload.llm}</code>
          </div>

          {planMutation.isError && <div className="error-box">{String(planMutation.error.message)}</div>}
          {planMutation.data && (
            <div className="command-preview">
              <span>Geplantes Kommando</span>
              <pre className="log-tail compact">{planMutation.data.command_text}</pre>
            </div>
          )}
        </div>

        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Letzter Review</h2>
              <p>{review?.exists ? `${review.reports.length} Kapitelreport(s)` : "Noch kein Review fuer diesen Stil"}</p>
            </div>
            <ListChecks size={22} />
          </div>

          {reviewQuery.isError && <div className="error-box">{String(reviewQuery.error.message)}</div>}
          {review?.exists ? (
            <>
              <div className="metric-grid">
                <Metric label="ERROR" value={summaryCounts.ERROR} tone={summaryCounts.ERROR ? "warn" : "ok"} />
                <Metric label="WARNING" value={summaryCounts.WARNING} tone={summaryCounts.WARNING ? "warn" : undefined} />
                <Metric label="INFO" value={summaryCounts.INFO} />
                <Metric label="Kapitel" value={review.reports.length} />
              </div>

              {review.summary_markdown && (
                <div className="command-preview">
                  <span>Summary</span>
                  <pre className="log-tail compact">{review.summary_markdown}</pre>
                </div>
              )}

              {selectedReport && (
                <div className="command-preview">
                  <span>Kapitelreport {selectedReport.chapter}</span>
                  <pre className="log-tail compact">{selectedReport.content || "(kein Markdown-Inhalt)"}</pre>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <ListChecks size={28} />
              <div>
                <h2>Kein Review-Report gefunden</h2>
                <p>Starte einen Review fuer den ausgewaehlten Stil oder wechsle den Stil.</p>
              </div>
            </div>
          )}

          <div className="panel-header slim">
            <div>
              <h2>Review-Fixes</h2>
              <p>Plan, Staging und Promote laufen ueber `apply_review_suggestions.py`.</p>
            </div>
          </div>

          {fixMutation.isError && <div className="error-box">{String(fixMutation.error.message)}</div>}
          <div className="action-row">
            <button className="button ghost" type="button" disabled={!style || fixMutation.isPending} onClick={() => fixMutation.mutate(fixPayload("plan"))}>
              Fix-Plan schreiben
            </button>
            <button className="button ghost" type="button" disabled={!style || fixMutation.isPending} onClick={() => fixMutation.mutate(fixPayload("stage"))}>
              Kandidaten stagen
            </button>
            <button className="button ghost" type="button" disabled={!style || fixMutation.isPending} onClick={() => fixMutation.mutate(fixPayload("promote"))}>
              Staged uebernehmen
            </button>
          </div>

          {review?.fixes.plan.content && (
            <div className="command-preview">
              <span>Fix-Plan</span>
              <pre className="log-tail compact">{review.fixes.plan.content}</pre>
            </div>
          )}
          {review?.fixes.manual_review.content && (
            <div className="command-preview">
              <span>Manuelle Befunde</span>
              <pre className="log-tail compact">{review.fixes.manual_review.content}</pre>
            </div>
          )}
          {review?.fixes.manifest.data && (
            <div className="command-preview">
              <span>Staging-Manifest</span>
              <pre className="log-tail compact">{JSON.stringify(review.fixes.manifest.data, null, 2)}</pre>
            </div>
          )}
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function buildReviewPayload(options: {
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

function ExportPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [style, setStyle] = useState(settings.active_style);
  const [scope, setScope] = useState("chapter");
  const [chapter, setChapter] = useState("");
  const [exportFormat, setExportFormat] = useState(settings.export_format);
  const [allowPartial, setAllowPartial] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, style || book?.style_mode],
    queryFn: () => getChapters(book!.id, style || book!.style_mode),
    enabled: Boolean(book)
  });
  const stylesQuery = useQuery({
    queryKey: ["styles", book?.id],
    queryFn: () => getBookStyles(book!.id),
    enabled: Boolean(book)
  });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: JOBS_REFETCH_INTERVAL_MS
  });
  const exportInfoQuery = useQuery({
    queryKey: ["exports", book?.id, style, scope, chapter],
    queryFn: () => getExportInfo(book!.id, style, scope, scope === "chapter" ? chapter : undefined),
    enabled: Boolean(book && style && (scope !== "chapter" || chapter))
  });
  const startMutation = useMutation({
    mutationFn: startExportJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });
  const planMutation = useMutation({ mutationFn: planAction });

  const chapters = chaptersQuery.data?.chapters ?? [];
  const jobs = jobsQuery.data?.jobs ?? [];
  const styleOptions = stylesQuery.data?.styles ?? [];
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : undefined;
  const stylesLoadError = stylesQuery.isError ? String(stylesQuery.error.message) : "";
  const exportInfo = exportInfoQuery.data;
  const exportContext = exportInfo?.context;
  const missingChapters = exportContext?.missing_chapters ?? [];

  useEffect(() => {
    setStyle(settings.active_style);
    setExportFormat(settings.export_format);
  }, [book?.id, settings]);

  useEffect(() => {
    const firstChapter = chapters[0]?.Kapitel;
    if (firstChapter && !chapter) {
      setChapter(firstChapter);
    }
  }, [chapter, chapters]);

  useEffect(() => {
    if (!selectedJob || selectedJob.running) {
      return;
    }
    if (["completed", "failed", "stopped", "stale"].includes(selectedJob.status)) {
      queryClient.invalidateQueries({ queryKey: ["exports", book?.id] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  }, [book?.id, queryClient, selectedJob?.job_id, selectedJob?.running, selectedJob?.status]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  const blockedByMissing = missingChapters.length > 0 && !allowPartial;
  const canStart = Boolean(style && exportFormat && (scope !== "chapter" || chapter) && !blockedByMissing);
  const payload = buildExportPayload({
    bookId: book.id,
    style,
    scope,
    chapter,
    exportFormat,
    allowPartial
  });

  return (
    <section className="page-stack">
      <PageHeader
        title="Export"
        description="Export-Laeufe aus React starten: Kapitel oder Buch, Format waehlen und den Lauf im globalen Job-Panel verfolgen."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Export konfigurieren</h2>
              <p>Startet `export_manuscript.py` als Hintergrundjob.</p>
            </div>
            <FileText size={22} />
          </div>

          <div className="form-grid">
            <label className="form-field">
              <span>Stil</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styleOptions.length === 0 && <option value={style}>{style || "Keine Styles geladen"}</option>}
                {styleOptions.map((item) => (
                  <option key={item.id} value={item.id}>{item.label || item.id}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Scope</span>
              <select value={scope} onChange={(event) => setScope(event.target.value)}>
                <option value="chapter">Kapitel</option>
                <option value="book">Ganzes Buch</option>
              </select>
            </label>

            {scope === "chapter" && (
              <label className="form-field">
                <span>Kapitel</span>
                <select value={chapter} onChange={(event) => setChapter(event.target.value)}>
                  {chapters.map((item) => (
                    <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel} / DE {item.DE}</option>
                  ))}
                </select>
              </label>
            )}

            <label className="form-field">
              <span>Format</span>
              <select value={exportFormat} onChange={(event) => setExportFormat(event.target.value)}>
                <option value="docx">DOCX</option>
                <option value="epub">EPUB</option>
                <option value="pdf">PDF</option>
                <option value="all">DOCX + EPUB</option>
              </select>
            </label>
          </div>

          {stylesLoadError && (
            <div className="error-box">
              API-Daten fehlen. Backend bitte neu starten. {stylesLoadError}
            </div>
          )}
          {exportInfoQuery.isError && (
            <div className="error-box">
              Export-Kontext konnte nicht geladen werden. {String(exportInfoQuery.error.message)}
            </div>
          )}

          <div className="toggle-row">
            <label>
              <input type="checkbox" checked={allowPartial} onChange={(event) => setAllowPartial(event.target.checked)} />
              <span>Teilweise vorhandene Kapitel/Szenen erlauben</span>
            </label>
          </div>

          {blockedByMissing && (
            <div className="error-box">
              Es fehlen deutsche Szenen in {missingChapters.slice(0, 12).join(", ")}{missingChapters.length > 12 ? " ..." : ""}. Aktiviere Teil-Export oder erzeuge die fehlenden Szenen.
            </div>
          )}
          {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}
          {planMutation.isError && <div className="error-box">{String(planMutation.error.message)}</div>}

          {exportContext && (
            <div className="metric-grid">
              <Metric label="Kapitel" value={exportContext.chapter_metrics.chapters} />
              <Metric label="DE-Szenen" value={exportContext.chapter_metrics.de_scenes} />
              <Metric label="Fehlend" value={exportContext.chapter_metrics.missing} tone={exportContext.chapter_metrics.missing ? "warn" : "ok"} />
              <Metric label="Exportbilder" value={exportContext.illustration_counts.total} />
            </div>
          )}

          {exportContext && (
            <div className="command-preview">
              <span>Export-Kontext</span>
              <pre className="log-tail compact">{[
                `Ausgabe: ${exportContext.output_root}`,
                `Cover: ${exportContext.cover_status}`,
                `Frontmatter: ${exportContext.front_enabled.length ? exportContext.front_enabled.join(", ") : "aus"}`,
                `Illustrationen: ${exportContext.illustrations_status} (${exportContext.illustration_counts.chapter} Kapitel / ${exportContext.illustration_counts.scene} Szenen)`,
                `Umfang: ${exportContext.selected_chapters.length} Kapitel`
              ].join("\n")}</pre>
            </div>
          )}

          <div className="action-row">
            <button className="button primary" type="button" disabled={!canStart || startMutation.isPending} onClick={() => startMutation.mutate(payload)}>
              <FileText size={16} />
              Export starten
            </button>
            <button className="button ghost" type="button" disabled={!style || !exportFormat || (scope === "chapter" && !chapter) || planMutation.isPending} onClick={() => planMutation.mutate(payload)}>
              Kommando planen
            </button>
            <code>{payload.scope}{payload.chapter ? ` / ${payload.chapter}` : ""} / {payload.export_format}</code>
          </div>

          {planMutation.data && (
            <div className="command-preview">
              <span>Geplantes Kommando</span>
              <pre className="log-tail compact">{planMutation.data.command_text}</pre>
            </div>
          )}

          {exportInfo && (
            <div className="command-preview">
              <span>Letzte Exportdateien</span>
              {exportInfo.latest_files.length > 0 ? (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Datei</th>
                        <th>Groesse</th>
                        <th>Geaendert</th>
                      </tr>
                    </thead>
                    <tbody>
                      {exportInfo.latest_files.map((file) => (
                        <tr key={file.path}>
                          <td><code>{file.path}</code></td>
                          <td>{formatBytes(file.size)}</td>
                          <td>{formatDateTime(file.modified_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="table-state">Noch keine Exportdateien fuer diesen Stil gefunden.</div>
              )}
            </div>
          )}
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function buildExportPayload(options: {
  bookId: string;
  style: string;
  scope: string;
  chapter: string;
  exportFormat: string;
  allowPartial: boolean;
}): ExportJobRequest {
  const payload: ExportJobRequest = {
    action: "export",
    book_id: options.bookId,
    style: options.style,
    scope: options.scope,
    export_format: options.exportFormat,
    allow_partial: options.allowPartial
  };
  if (options.scope === "chapter") {
    payload.chapter = options.chapter;
  }
  return payload;
}

function ImagesPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [style, setStyle] = useState(settings.active_style);
  const [scope, setScope] = useState<"chapter" | "range">("chapter");
  const [kind, setKind] = useState<"scene" | "chapter" | "both">("scene");
  const [chapter, setChapter] = useState("");
  const [startChapter, setStartChapter] = useState("");
  const [endChapter, setEndChapter] = useState("");
  const [backend, setBackend] = useState<"auto" | "cli" | "api">("auto");
  const [quality, setQuality] = useState("");
  const [aspectRatio, setAspectRatio] = useState("");
  const [missing, setMissing] = useState(true);
  const [overwrite, setOverwrite] = useState(false);
  const [dryRun, setDryRun] = useState(true);
  const [noReference, setNoReference] = useState(false);
  const [allowPaidGeneration, setAllowPaidGeneration] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const chaptersQuery = useQuery({
    queryKey: ["chapters", book?.id, style || book?.style_mode],
    queryFn: () => getChapters(book!.id, style || book!.style_mode),
    enabled: Boolean(book)
  });
  const stylesQuery = useQuery({
    queryKey: ["styles", book?.id],
    queryFn: () => getBookStyles(book!.id),
    enabled: Boolean(book)
  });
  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => getJobs(12),
    refetchInterval: JOBS_REFETCH_INTERVAL_MS
  });
  const startMutation = useMutation({
    mutationFn: startIllustrationBatchJob,
    onSuccess: (data) => {
      setSelectedJobId(data.job.job_id);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });
  const planMutation = useMutation({ mutationFn: planAction });

  const chapters = chaptersQuery.data?.chapters ?? [];
  const jobs = jobsQuery.data?.jobs ?? [];
  const styleOptions = stylesQuery.data?.styles ?? [];
  const selectedJob = selectedJobId ? jobs.find((job) => job.job_id === selectedJobId) : undefined;

  useEffect(() => {
    setStyle(settings.active_style);
  }, [book?.id, settings.active_style]);

  useEffect(() => {
    const firstChapter = chapters[0]?.Kapitel;
    if (firstChapter) {
      if (!chapter) setChapter(firstChapter);
      if (!startChapter) setStartChapter(firstChapter);
      if (!endChapter) setEndChapter(firstChapter);
    }
  }, [chapter, chapters, endChapter, startChapter]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  const payload = buildIllustrationPayload({
    bookId: book.id,
    style,
    kind,
    scope,
    chapter,
    startChapter,
    endChapter,
    backend,
    quality,
    aspectRatio,
    missing,
    overwrite,
    dryRun,
    noReference,
    allowPaidGeneration
  });
  const canStart = Boolean(style && kind && (scope === "chapter" ? chapter : startChapter));

  return (
    <section className="page-stack">
      <PageHeader
        title="Bilder"
        description="Higgsfield-Illustrationen fuer Kapitel und Szenen als Dashboard-Job vorbereiten oder starten."
      />
      <ContextBar book={book} settings={settings} selectedJob={selectedJob} />
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Higgsfield konfigurieren</h2>
              <p>Startet `generate_illustration_batch.py` und nutzt darunter die bestehende Einzelbild-CLI.</p>
            </div>
            <Image size={22} />
          </div>

          <div className="form-grid">
            <label className="form-field">
              <span>Stil</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styleOptions.length === 0 && <option value={style}>{style || "Keine Styles geladen"}</option>}
                {styleOptions.map((item) => (
                  <option key={item.id} value={item.id}>{item.label || item.id}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Bildtyp</span>
              <select value={kind} onChange={(event) => setKind(event.target.value as "scene" | "chapter" | "both")}>
                <option value="scene">Szenenbilder</option>
                <option value="chapter">Kapitelbilder</option>
                <option value="both">Kapitel + Szenen</option>
              </select>
            </label>

            <label className="form-field">
              <span>Umfang</span>
              <select value={scope} onChange={(event) => setScope(event.target.value as "chapter" | "range")}>
                <option value="chapter">Ein Kapitel</option>
                <option value="range">Kapitelbereich</option>
              </select>
            </label>

            {scope === "chapter" ? (
              <label className="form-field">
                <span>Kapitel</span>
                <select value={chapter} onChange={(event) => setChapter(event.target.value)}>
                  {chapters.map((item) => (
                    <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel} / DE {item.DE}</option>
                  ))}
                </select>
              </label>
            ) : (
              <>
                <label className="form-field">
                  <span>Von</span>
                  <select value={startChapter} onChange={(event) => setStartChapter(event.target.value)}>
                    {chapters.map((item) => (
                      <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>
                    ))}
                  </select>
                </label>
                <label className="form-field">
                  <span>Bis</span>
                  <select value={endChapter} onChange={(event) => setEndChapter(event.target.value)}>
                    {chapters.map((item) => (
                      <option key={item.Kapitel} value={item.Kapitel}>{item.Kapitel}</option>
                    ))}
                  </select>
                </label>
              </>
            )}

            <label className="form-field">
              <span>Backend</span>
              <select value={backend} onChange={(event) => setBackend(event.target.value as "auto" | "cli" | "api")}>
                <option value="auto">Auto</option>
                <option value="cli">CLI</option>
                <option value="api">API</option>
              </select>
            </label>

            <label className="form-field">
              <span>Qualitaet</span>
              <input value={quality} onChange={(event) => setQuality(event.target.value)} placeholder="Default aus book.yaml" />
            </label>

            <label className="form-field">
              <span>Seitenverhaeltnis</span>
              <input value={aspectRatio} onChange={(event) => setAspectRatio(event.target.value)} placeholder="z. B. 2:3" />
            </label>
          </div>

          <div className="toggle-row">
            <label>
              <input type="checkbox" checked={missing} onChange={(event) => setMissing(event.target.checked)} />
              <span>Vorhandene Bilder ueberspringen</span>
            </label>
            <label>
              <input type="checkbox" checked={overwrite} onChange={(event) => setOverwrite(event.target.checked)} />
              <span>Vorhandene Bilder ersetzen</span>
            </label>
            <label>
              <input type="checkbox" checked={dryRun} onChange={(event) => setDryRun(event.target.checked)} />
              <span>Dry-run</span>
            </label>
            <label>
              <input type="checkbox" checked={noReference} onChange={(event) => setNoReference(event.target.checked)} />
              <span>Ohne Moodboard/Referenz generieren</span>
            </label>
            <label>
              <input type="checkbox" checked={allowPaidGeneration} onChange={(event) => setAllowPaidGeneration(event.target.checked)} />
              <span>Bezahlte API-Generierung erlauben</span>
            </label>
          </div>

          {startMutation.isError && <div className="error-box">{String(startMutation.error.message)}</div>}
          {planMutation.isError && <div className="error-box">{String(planMutation.error.message)}</div>}

          <div className="action-row">
            <button className="button primary" type="button" disabled={!canStart || startMutation.isPending} onClick={() => startMutation.mutate(payload)}>
              <Image size={16} />
              Bilder-Job starten
            </button>
            <button className="button ghost" type="button" disabled={!canStart || planMutation.isPending} onClick={() => planMutation.mutate(payload)}>
              Kommando planen
            </button>
            <code>{payload.kind} / {payload.scope}{payload.dry_run ? " / dry-run" : ""}</code>
          </div>

          {planMutation.data && (
            <div className="command-preview">
              <span>Geplantes Kommando</span>
              <pre className="log-tail compact">{planMutation.data.command_text}</pre>
            </div>
          )}
        </div>

        <JobPanel
          jobs={jobs}
          loading={jobsQuery.isLoading}
          selectedJobId={selectedJobId ?? jobs[0]?.job_id ?? null}
          onSelectJob={setSelectedJobId}
        />
      </div>
    </section>
  );
}

function buildIllustrationPayload(options: {
  bookId: string;
  style: string;
  kind: "scene" | "chapter" | "both";
  scope: "chapter" | "range";
  chapter: string;
  startChapter: string;
  endChapter: string;
  backend: "auto" | "cli" | "api";
  quality: string;
  aspectRatio: string;
  missing: boolean;
  overwrite: boolean;
  dryRun: boolean;
  noReference: boolean;
  allowPaidGeneration: boolean;
}): IllustrationBatchRequest {
  const payload: IllustrationBatchRequest = {
    action: "illustration_batch",
    book_id: options.bookId,
    style: options.style,
    kind: options.kind,
    scope: options.scope,
    backend: options.backend,
    missing: options.missing,
    overwrite: options.overwrite,
    dry_run: options.dryRun,
    no_reference: options.noReference,
    allow_paid_generation: options.allowPaidGeneration
  };
  if (options.scope === "chapter") {
    payload.chapter = options.chapter;
  } else {
    payload.start_chapter = options.startChapter;
    payload.end_chapter = options.endChapter;
  }
  if (options.quality.trim()) {
    payload.quality = options.quality.trim();
  }
  if (options.aspectRatio.trim()) {
    payload.aspect_ratio = options.aspectRatio.trim();
  }
  return payload;
}

function NamesPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const queryClient = useQueryClient();
  const [rows, setRows] = useState<NameRow[]>([]);
  const namesQuery = useQuery({
    queryKey: ["names", book?.id],
    queryFn: () => getBookNames(book!.id),
    enabled: Boolean(book)
  });
  const saveMutation = useMutation({
    mutationFn: (nextRows: NameRow[]) => saveBookNames(book!.id, nextRows),
    onSuccess: (data) => {
      setRows(data.names);
      queryClient.invalidateQueries({ queryKey: ["names", book?.id] });
    }
  });
  const names = namesQuery.data?.names ?? [];
  const totals = useMemo(() => summarizeNames(rows), [rows]);
  const validationErrors = useMemo(() => validateNameRows(rows), [rows]);

  useEffect(() => {
    setRows(names);
  }, [book?.id, namesQuery.data]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  return (
    <section className="page-stack">
      <PageHeader
        title="Namen"
        description="Buchlokale Namen- und Begriffsliste aus `names.yaml` bearbeiten und speichern."
      />
      <ContextBar book={book} settings={settings} />
      <div className="panel stack-panel">
        <div className="panel-header">
          <div>
            <h2>Namenliste</h2>
            <p>{namesQuery.isLoading ? "Eintraege werden geladen..." : `${rows.length} Eintraege geladen`}</p>
          </div>
          <NotebookTabs size={22} />
        </div>
        <div className="metric-grid">
          <Metric label="Eintraege" value={names.length} />
          <Metric label="Personen" value={totals.person} />
          <Metric label="Genehmigt" value={totals.approved} tone={totals.approved ? "ok" : undefined} />
          <Metric label="Entwurf" value={totals.draft} tone={totals.draft ? "warn" : undefined} />
        </div>
        {namesQuery.isError && <div className="error-box">{String(namesQuery.error.message)}</div>}
        {saveMutation.isError && <div className="error-box">{String(saveMutation.error.message)}</div>}
        {validationErrors.length > 0 && (
          <div className="error-box">{validationErrors.slice(0, 4).join(" · ")}</div>
        )}
        <NamesEditor
          names={rows}
          loading={namesQuery.isLoading}
          onChange={setRows}
        />
        <div className="action-row">
          <button
            className="button primary"
            type="button"
            disabled={namesQuery.isLoading || saveMutation.isPending || validationErrors.length > 0}
            onClick={() => saveMutation.mutate(rows)}
          >
            Speichern
          </button>
          <button className="button ghost" type="button" disabled={namesQuery.isLoading || saveMutation.isPending} onClick={() => setRows(names)}>
            Zuruecksetzen
          </button>
          <button className="button ghost" type="button" onClick={() => setRows([...rows, emptyNameRow()])}>
            Eintrag hinzufuegen
          </button>
          {saveMutation.isSuccess && <code>Gespeichert</code>}
        </div>
      </div>
    </section>
  );
}

function NamesEditor({ names, loading, onChange }: { names: NameRow[]; loading: boolean; onChange: (rows: NameRow[]) => void }) {
  if (loading) {
    return <div className="table-state">Namen werden geladen...</div>;
  }
  if (!names.length) {
    return (
      <div className="empty-state compact">
        <NotebookTabs size={20} />
        <span>Diese Namenliste enthaelt aktuell keine Eintraege.</span>
      </div>
    );
  }
  const update = (index: number, key: keyof NameRow, value: string) => {
    onChange(names.map((row, rowIndex) => rowIndex === index ? { ...row, [key]: value } : row));
  };
  const remove = (index: number) => {
    onChange(names.filter((_row, rowIndex) => rowIndex !== index));
  };
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Quelle</th>
            <th>Ziel</th>
            <th>Aliasse</th>
            <th>Typ</th>
            <th>Status</th>
            <th>Notiz</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {names.map((row, index) => (
            <tr key={`${row.source}-${row.target}-${index}`}>
              <td><input className="table-input" value={row.source} onChange={(event) => update(index, "source", event.target.value)} /></td>
              <td><input className="table-input" value={row.target} onChange={(event) => update(index, "target", event.target.value)} /></td>
              <td><input className="table-input" value={row.aliases} onChange={(event) => update(index, "aliases", event.target.value)} /></td>
              <td>
                <select className="table-input" value={row.type} onChange={(event) => update(index, "type", event.target.value)}>
                  <option value="person">person</option>
                  <option value="place">place</option>
                  <option value="term">term</option>
                  <option value="title">title</option>
                </select>
              </td>
              <td>
                <select className="table-input" value={row.status} onChange={(event) => update(index, "status", event.target.value)}>
                  <option value="draft">draft</option>
                  <option value="approved">approved</option>
                  <option value="review">review</option>
                </select>
              </td>
              <td><input className="table-input wide" value={row.note} onChange={(event) => update(index, "note", event.target.value)} /></td>
              <td>
                <button className="icon-button small" type="button" aria-label="Eintrag entfernen" onClick={() => remove(index)}>
                  <X size={15} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function emptyNameRow(): NameRow {
  return { source: "", target: "", aliases: "", type: "person", status: "draft", note: "" };
}

function validateNameRows(names: NameRow[]): string[] {
  const errors: string[] = [];
  names.forEach((row, index) => {
    const source = row.source.trim();
    const target = row.target.trim();
    if (!source && !target) {
      return;
    }
    if (!source) {
      errors.push(`Zeile ${index + 1}: Quelle fehlt`);
    }
    if (!target) {
      errors.push(`Zeile ${index + 1}: Ziel fehlt`);
    }
  });
  return errors;
}

function summarizeNames(names: NameRow[]) {
  return names.reduce(
    (acc, row) => ({
      person: acc.person + (row.type === "person" ? 1 : 0),
      approved: acc.approved + (row.status === "approved" ? 1 : 0),
      draft: acc.draft + (row.status === "draft" ? 1 : 0)
    }),
    { person: 0, approved: 0, draft: 0 }
  );
}

function LogsPage({ book, settings }: { book?: BookSummary; settings: WorkspaceSettings }) {
  const [searchParams] = useSearchParams();
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState("all");
  const [kindFilter, setKindFilter] = useState("all");
  const [query, setQuery] = useState("");
  const logsQuery = useQuery({
    queryKey: ["logs", book?.id],
    queryFn: () => getLogs(book?.id, 80),
    enabled: Boolean(book)
  });
  const logDetailQuery = useQuery({
    queryKey: ["log", selectedLogId],
    queryFn: () => getLog(selectedLogId!, 400),
    enabled: Boolean(selectedLogId)
  });
  const logs = logsQuery.data?.logs ?? [];
  const filteredLogs = useMemo(
    () => filterLogs(logs, sourceFilter, kindFilter, query),
    [logs, sourceFilter, kindFilter, query]
  );
  const selectedLog = selectedLogId ? (logs.find((item) => item.id === selectedLogId) ?? filteredLogs[0]) : filteredLogs[0];

  useEffect(() => {
    const requestedLog = searchParams.get("log");
    if (requestedLog) {
      setSelectedLogId(requestedLog);
    }
  }, [searchParams]);

  useEffect(() => {
    const requestedLog = searchParams.get("log");
    if (requestedLog) {
      return;
    }
    if (!filteredLogs.length) {
      setSelectedLogId(null);
      return;
    }
    if (!selectedLogId || !filteredLogs.some((item) => item.id === selectedLogId)) {
      setSelectedLogId(filteredLogs[0].id);
    }
  }, [filteredLogs, selectedLogId]);

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  return (
    <section className="page-stack">
      <PageHeader
        title="Logs"
        description="Dashboard-Joblogs und buchlokale Statuslogs lesend durchsuchen. Dieser Slice schreibt keine Logdateien."
      />
      <ContextBar book={book} settings={settings} />
      <div className="workflow-grid">
        <div className="panel stack-panel">
          <div className="panel-header">
            <div>
              <h2>Logliste</h2>
              <p>{logsQuery.isLoading ? "Logs werden geladen..." : `${filteredLogs.length}/${logs.length} Logs`}</p>
            </div>
            <ScrollText size={22} />
          </div>
          <div className="form-grid compact-grid">
            <label className="form-field">
              <span>Quelle</span>
              <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
                <option value="all">Alle Quellen</option>
                <option value="dashboard-job">Dashboard-Jobs</option>
                <option value="book-status">Buchstatus</option>
              </select>
            </label>
            <label className="form-field">
              <span>Jobtyp</span>
              <select value={kindFilter} onChange={(event) => setKindFilter(event.target.value)}>
                <option value="all">Alle Typen</option>
                <option value="batch">Translate</option>
                <option value="review">Review</option>
                <option value="export">Export</option>
              </select>
            </label>
            <label className="form-field wide">
              <span>Suche</span>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Dateiname oder Pfad" />
            </label>
          </div>
          {logsQuery.isError && <div className="error-box">{String(logsQuery.error.message)}</div>}
          <LogsTable logs={filteredLogs} selectedLogId={selectedLog?.id ?? null} loading={logsQuery.isLoading} onSelectLog={setSelectedLogId} />
        </div>

        <aside className="panel job-panel">
          <div className="panel-header">
            <div>
              <h2>Logdetail</h2>
              <p>{selectedLog?.path ?? "Kein Log ausgewaehlt"}</p>
            </div>
            <FileText size={21} />
          </div>
          {logDetailQuery.isError && <div className="error-box">{String(logDetailQuery.error.message)}</div>}
          {selectedLog ? (
            <>
              <div className="progress-line">
                <span>{selectedLog.source}</span>
                <strong>{formatBytes(selectedLog.size)}</strong>
              </div>
              <LogContent text={logDetailQuery.data?.content ?? "Log wird geladen..."} large />
              {logDetailQuery.data?.truncated && <div className="table-state">Anzeige auf die letzten 400 Zeilen begrenzt.</div>}
            </>
          ) : (
            <div className="empty-state compact">
              <PauseCircle size={24} />
              <span>Kein Log ausgewaehlt.</span>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}

function LogsTable({
  logs,
  selectedLogId,
  loading,
  onSelectLog
}: {
  logs: LogItem[];
  selectedLogId: string | null;
  loading: boolean;
  onSelectLog: (logId: string) => void;
}) {
  if (loading) {
    return <div className="table-state">Logs werden geladen...</div>;
  }
  if (!logs.length) {
    return <div className="table-state">Keine Logs fuer dieses Buch gefunden.</div>;
  }
  return (
    <div className="log-list-table">
      {logs.map((item) => (
        <button
          key={item.id}
          type="button"
          className={`job-row ${item.id === selectedLogId ? "selected" : ""}`}
          onClick={() => onSelectLog(item.id)}
          title={item.path}
        >
          <span className={`status-dot ${item.source === "dashboard-job" ? "running" : "completed"}`} />
          <span>
            <strong>{item.name}</strong>
            <small>{item.path}</small>
          </span>
          <em>{formatBytes(item.size)}</em>
        </button>
      ))}
    </div>
  );
}

function filterLogs(logs: LogItem[], sourceFilter: string, kindFilter: string, query: string): LogItem[] {
  const needle = query.trim().toLowerCase();
  return logs.filter((item) => {
    const sourceMatches = sourceFilter === "all" || item.source === sourceFilter;
    const kindMatches = kindFilter === "all" || logKind(item) === kindFilter;
    const queryMatches = !needle || `${item.name} ${item.path}`.toLowerCase().includes(needle);
    return sourceMatches && kindMatches && queryMatches;
  });
}

function logKind(item: LogItem): string {
  const text = `${item.name} ${item.path}`.toLowerCase();
  if (text.includes("-review-")) {
    return "review";
  }
  if (text.includes("-export-")) {
    return "export";
  }
  if (text.includes("-batch-") || text.includes("-translate-")) {
    return "batch";
  }
  return "other";
}

function LogContent({ text, large = false }: { text: string; large?: boolean }) {
  return (
    <pre className={`log-tail ${large ? "large" : ""}`}>
      {text.split("\n").map((line, index) => (
        <span key={`${index}-${line.slice(0, 16)}`} className={logLineClass(line)}>
          {line || " "}
          {"\n"}
        </span>
      ))}
    </pre>
  );
}

function logLineClass(line: string): string {
  const lower = line.toLowerCase();
  if (lower.includes("fehler") || lower.includes("error") || lower.includes("failed") || lower.includes("prompt-echo")) {
    return "log-line error";
  }
  if (lower.includes("warning") || lower.includes("warnung") || lower.includes("llm_review_failed")) {
    return "log-line warning";
  }
  return "log-line";
}

function formatBytes(value: number): string {
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${Math.round(value / 1024)} KB`;
  }
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(date);
}

function SettingsPage({
  book,
  settings,
  onSettingsChange
}: {
  book?: BookSummary;
  settings: WorkspaceSettings;
  onSettingsChange: (settings: WorkspaceSettings) => void;
}) {
  const queryClient = useQueryClient();
  const stylesQuery = useQuery({
    queryKey: ["styles", book?.id],
    queryFn: () => getBookStyles(book!.id),
    enabled: Boolean(book)
  });
  const modelsQuery = useQuery({ queryKey: ["models"], queryFn: getModels });
  const saveMutation = useMutation({
    mutationFn: () => saveBookSettings(book!.id, {
      active_style: settings.active_style,
      translate_provider: settings.translate_provider,
      translate_model: settings.translate_model,
      chunk_char_limit: settings.chunk_char_limit
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["books"] });
      queryClient.invalidateQueries({ queryKey: ["styles", book?.id] });
      queryClient.invalidateQueries({ queryKey: ["chapters", book?.id] });
    }
  });
  const styleOptions = stylesQuery.data?.styles ?? [];
  const models = modelsQuery.data?.models ?? [];
  const update = (patch: Partial<WorkspaceSettings>) => onSettingsChange({ ...settings, ...patch });

  if (!book) {
    return <div className="boot-screen">Kein Buch geladen.</div>;
  }

  return (
    <section className="page-stack">
      <PageHeader
        title="Buch-Settings"
        description="Arbeitskontext fuer dieses Buch. Aenderungen wirken sofort lokal; erst Speichern schreibt Produktionsdefaults in `book.yaml`."
      />
      <ContextBar book={book} settings={settings} />
      <div className="panel stack-panel">
        <div className="panel-header">
          <div>
            <h2>Arbeitskontext</h2>
            <p>Gespeichert pro Buch im Browser-LocalStorage.</p>
          </div>
          <Settings size={22} />
        </div>

        <div className="form-grid">
          <label className="form-field">
            <span>Aktiver Stil</span>
            <select value={settings.active_style} onChange={(event) => update({ active_style: event.target.value })}>
              {styleOptions.length === 0 && <option value={settings.active_style}>{settings.active_style}</option>}
              {styleOptions.map((item) => (
                <option key={item.id} value={item.id}>{item.label || item.id}</option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Uebersetzungsprovider</span>
            <select value={settings.translate_provider} onChange={(event) => update({ translate_provider: event.target.value })}>
              <option value="openrouter">OpenRouter</option>
              <option value="ollama">Ollama</option>
              <option value="prompt_file">Prompt-Datei</option>
              <option value="workspace_ai">Workspace-KI</option>
            </select>
          </label>

          <label className="form-field wide">
            <span>OpenRouter-Modell fuer Uebersetzung</span>
            <select value={settings.translate_model} onChange={(event) => update({ translate_model: event.target.value })}>
              {models.length === 0 && <option value={settings.translate_model}>{settings.translate_model || "Keine Modelle geladen"}</option>}
              {models.map((item) => (
                <option key={item.id} value={item.id}>{item.name ? `${item.name} (${item.provider})` : item.id}</option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Ollama-Modell fuer Uebersetzung</span>
            <input value={settings.translate_ollama_model} onChange={(event) => update({ translate_ollama_model: event.target.value })} />
          </label>

          <label className="form-field">
            <span>Chunk-Grenze</span>
            <input
              type="number"
              min="1000"
              step="500"
              value={settings.chunk_char_limit}
              onChange={(event) => update({ chunk_char_limit: Number(event.target.value) })}
            />
          </label>

          <label className="form-field">
            <span>Review-LLM</span>
            <select value={settings.review_llm} onChange={(event) => update({ review_llm: event.target.value })}>
              <option value="none">Nur Regelcheck</option>
              <option value="openrouter">OpenRouter</option>
              <option value="ollama">Ollama</option>
            </select>
          </label>

          <label className="form-field">
            <span>Review-Scope</span>
            <select value={settings.review_llm_scope} onChange={(event) => update({ review_llm_scope: event.target.value })}>
              <option value="flagged">Nur markierte Szenen</option>
              <option value="all">Alle Szenen</option>
            </select>
          </label>

          <label className="form-field wide">
            <span>OpenRouter-Modell fuer Review</span>
            <select value={settings.review_model} onChange={(event) => update({ review_model: event.target.value })}>
              {models.length === 0 && <option value={settings.review_model}>{settings.review_model || "Keine Modelle geladen"}</option>}
              {models.map((item) => (
                <option key={item.id} value={item.id}>{item.name ? `${item.name} (${item.provider})` : item.id}</option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Ollama-Modell fuer Review</span>
            <input value={settings.review_ollama_model} onChange={(event) => update({ review_ollama_model: event.target.value })} />
          </label>

          <label className="form-field">
            <span>Exportformat</span>
            <select value={settings.export_format} onChange={(event) => update({ export_format: event.target.value })}>
              <option value="docx">DOCX</option>
              <option value="epub">EPUB</option>
              <option value="pdf">PDF</option>
              <option value="all">DOCX + EPUB</option>
            </select>
          </label>
        </div>

        {(stylesQuery.isError || modelsQuery.isError) && (
          <div className="error-box">
            API-Daten konnten nicht geladen werden. {String(stylesQuery.error?.message ?? modelsQuery.error?.message)}
          </div>
        )}
        {saveMutation.isError && <div className="error-box">{String(saveMutation.error.message)}</div>}
        {saveMutation.isSuccess && (
          <div className="success-box">
            Gespeichert in `books/{book.id}/book.yaml`: Stil, Provider, OpenRouter-Modell und Chunk-Grenze.
          </div>
        )}

        <div className="action-row">
          <button className="button primary" type="button" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
            <FileText size={16} />
            In book.yaml speichern
          </button>
          <button className="button secondary" type="button" onClick={() => onSettingsChange(defaultWorkspaceSettings(book))}>
            <RefreshCw size={16} />
            Auf Buchdefault zuruecksetzen
          </button>
          <code>{settings.active_style} / {settings.translate_provider}</code>
        </div>
      </div>
      <div className="empty-state">
        <Settings size={28} />
        <div>
          <h2>Wo diese Settings wirken</h2>
          <p>Uebersicht, Uebersetzen, Review und Export verwenden diese Werte als aktiven React-Arbeitskontext. Der Speichern-Button schreibt nur buchnahe Produktionsdefaults in `book.yaml`; Review- und Export-Auswahl bleiben lokale UI-Voreinstellungen.</p>
        </div>
      </div>
    </section>
  );
}

function PlaceholderWorkflow({ title, book }: { title: string; book?: BookSummary }) {
  return (
    <section className="page-stack">
      <PageHeader
        title={title}
        description="Dieser Workflow wird nach dem Uebersicht- und Job-Panel-Meilenstein portiert."
      />
      {book && <ContextBar book={book} />}
      <div className="empty-state">
        <Activity size={28} />
        <div>
          <h2>{title} bleibt vorerst in Streamlit</h2>
          <p>Die React-Version zeigt hier bewusst noch kein halbfertiges Formular. Parameter und Aktionen werden spaeter direkt im Workflow platziert.</p>
        </div>
      </div>
    </section>
  );
}

function summarizeChapters(chapters: ChapterRow[]) {
  return chapters.reduce(
    (acc, chapter) => ({
      source: acc.source + Number(chapter.RU || 0),
      de: acc.de + Number(chapter.DE || 0),
      missing: acc.missing + Number(chapter.Fehlt || 0)
    }),
    { source: 0, de: 0, missing: 0 }
  );
}
