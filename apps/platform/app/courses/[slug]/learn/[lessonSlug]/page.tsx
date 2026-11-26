"use client";

import Link from "next/link";
import { use, useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, CheckCircle2, ChevronDown, Clipboard, Minus, PanelLeftClose, PanelLeftOpen, Plus, SunMoon, X } from "lucide-react";
import { ThemeSwitcher } from "@/components/theme-provider";
import { useI18n } from "@/lib/i18n";

type Lesson = { id: string; title: string; slug: string; description?: string; content_en: string; content_mm?: string | null; duration_minutes?: number; code_examples?: { id: string; title: string; language: string; code: string; filename?: string | null }[] };
type LearningLesson = { id: string; title: string; slug: string; duration_minutes: number };
type Learning = { title?: string; modules: { id?: string; title: string; lessons: LearningLesson[] }[] };
type Quiz = { title: string; explanation?: string; questions: { id: string; prompt: string; options: string[]; question_type: string }[]; latest_attempt?: { score: number; total: number } | null };
const csrf = () => document.cookie.match(/(?:^|; )cm_csrf=([^;]+)/)?.[1] ?? "";

function ContentBlocks({ content }: { content: string }) {
  const blocks = content.split(/\n\s*\n/).map(block => block.trim()).filter(Boolean);
  const tableCells = (line: string) => line.replace(/^\||\|$/g, "").split("|").map(cell => cell.trim());

  return <div className="space-y-6">
    {blocks.map((block, index) => {
      const lines = block.split("\n");
      const first = lines[0];
      const heading = first.match(/^(#{1,3})\s+(.+)$/);
      const codeFence = first.match(/^```\s*([\w+-]*)$/);
      const calloutMatch = first.match(/^:::(TIP|NOTE|WARNING)$/i);
      const inlineCalloutMatch = first.match(/^!\s*(TIP|NOTE|WARNING):\s*(.*)$/i);
      const callout = Boolean((calloutMatch && lines.at(-1) === ":::") || inlineCalloutMatch);
      const table = lines.length >= 2 && /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(lines[1]);

      if (heading) {
        const Heading = heading[1].length === 3 ? "h3" : "h2";
        return <section key={index} className="space-y-3 pt-3"><Heading className={heading[1].length === 3 ? "text-xl font-semibold text-foreground" : heading[1].length === 2 ? "text-2xl font-semibold text-foreground" : "text-3xl font-semibold text-foreground"}>{heading[2]}</Heading>{lines.length > 1 && <p className="whitespace-pre-line text-[17px] leading-[1.8] text-muted">{lines.slice(1).join("\n")}</p>}</section>;
      }

      if (codeFence && lines.at(-1) === "```") return <pre key={index} className="overflow-x-auto rounded-2xl border border-line bg-[#0D1628] p-5 text-sm leading-7 text-indigo-100"><code>{lines.slice(1, -1).join("\n")}</code></pre>;
      if (callout) {
        const tone = (calloutMatch?.[1] || inlineCalloutMatch?.[1] || "note").toLowerCase();
        const body = inlineCalloutMatch ? [inlineCalloutMatch[2], ...lines.slice(1)] : lines.slice(1, -1);
        return <aside key={index} className={`rounded-xl border-l-4 px-5 py-4 text-[17px] leading-[1.8] ${tone === "warning" ? "border-amber-500 bg-amber-500/10 text-amber-900 dark:text-amber-100" : "border-primary bg-primary/8 text-muted"}`}><p className="mb-2 text-xs font-semibold uppercase tracking-[.16em]">{tone}</p>{body.filter(Boolean).map((line, lineIndex) => <p key={lineIndex}>{line}</p>)}</aside>;
      }
      if (table) {
        return <div key={index} className="overflow-x-auto rounded-xl border border-line"><table className="min-w-full text-left text-sm"><thead className="bg-surface-elevated/60 text-foreground"><tr>{tableCells(lines[0]).map((cell, cellIndex) => <th key={cellIndex} className="border-b border-line px-4 py-3 font-semibold">{cell}</th>)}</tr></thead><tbody>{lines.slice(2).map((line, rowIndex) => <tr key={rowIndex} className="border-b border-line last:border-0">{tableCells(line).map((cell, cellIndex) => <td key={cellIndex} className="px-4 py-3 text-muted">{cell}</td>)}</tr>)}</tbody></table></div>;
      }
      if (/^!\s*IMAGE:\s*(\/[^\s]+)$/i.test(first) && lines.length === 1) {
        const src = first.replace(/^!\s*IMAGE:\s*/i, "").trim();
        return <figure key={index}><img src={src} alt="Lesson illustration" className="max-h-[520px] w-full rounded-2xl border border-line object-contain" /></figure>;
      }
      if (/^!\[[^\]]*\]\((\/[^)]+)\)$/.test(first) && lines.length === 1) {
        const image = first.match(/^!\[([^\]]*)\]\((\/[^)]+)\)$/);
        return image ? <figure key={index} className="space-y-2"><img src={image[2]} alt={image[1]} className="max-h-[520px] w-full rounded-2xl border border-line object-contain" /><figcaption className="text-center text-xs text-muted">{image[1]}</figcaption></figure> : null;
      }
      if (lines.every(line => /^[-*]\s/.test(line))) return <ul key={index} className="list-disc space-y-2 pl-6 text-[17px] leading-[1.8] text-muted">{lines.map((line, lineIndex) => <li key={lineIndex}>{line.replace(/^[-*]\s+/, "")}</li>)}</ul>;
      if (lines.every(line => /^\d+\.\s/.test(line))) return <ol key={index} className="list-decimal space-y-2 pl-6 text-[17px] leading-[1.8] text-muted">{lines.map((line, lineIndex) => <li key={lineIndex}>{line.replace(/^\d+\.\s+/, "")}</li>)}</ol>;
      if (/^>\s?/.test(first)) return <aside key={index} className="rounded-xl border-l-4 border-primary bg-primary/8 px-5 py-4 text-[17px] leading-[1.8] text-muted">{lines.map((line, lineIndex) => <p key={lineIndex}>{line.replace(/^>\s?/, "")}</p>)}</aside>;
      if (/^(---|\*\s*\*\s*\*)$/.test(first) && lines.length === 1) return <hr key={index} className="border-line" />;
      return <p key={index} className="whitespace-pre-line text-[17px] leading-[1.8] text-muted">{block}</p>;
    })}
  </div>;
}

function CodeExample({ example }: { example: NonNullable<Lesson["code_examples"]>[number] }) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(example.code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  return <section className="overflow-hidden rounded-2xl border border-line bg-[#0D1628]" aria-label={`${example.language} code example`}><div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3 text-xs"><span className="font-medium text-slate-200">{example.filename || example.title}</span><div className="flex items-center gap-3"><span className="uppercase tracking-[.14em] text-slate-400">{example.language}</span><button type="button" onClick={copy} className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-2.5 py-1.5 text-slate-300 transition hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-400/70"><Clipboard size={14} aria-hidden="true" /> {copied ? t("copied") : t("copy")}</button></div></div><pre className="max-w-full overflow-x-auto p-5 text-sm leading-7 text-indigo-100"><code>{example.code}</code></pre></section>;
}

function LessonQuiz({ lessonId }: { lessonId: string }) {
  const { t } = useI18n();
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{ score: number; total: number } | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => { fetch(`/api/v1/me/lessons/${lessonId}/quiz`, { credentials: "include" }).then(response => response.ok ? response.json() : null).then(value => { if (value) { setQuiz(value); setResult(value.latest_attempt ?? null); } }).catch(() => undefined); }, [lessonId]);

  async function submit() {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch(`/api/v1/me/lessons/${lessonId}/quiz`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() }, body: JSON.stringify({ answers }) });
      const value = await response.json().catch(() => ({}));
      if (response.ok) setResult(value);
      else if (response.status === 401) setMessage("Sign in and enroll to submit this quiz.");
      else setMessage(value.detail || "Unable to submit quiz.");
    } finally {
      setBusy(false);
    }
  }

  if (!quiz) return null;
  return <section className="mt-12 rounded-2xl border border-line bg-surface p-5 sm:p-7" aria-labelledby="lesson-quiz-title"><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">{t("knowledgeCheck")}</p><h2 id="lesson-quiz-title" className="mt-2 text-2xl font-semibold text-foreground">{quiz.title}</h2>{quiz.explanation && <p className="mt-3 text-sm leading-7 text-muted">{quiz.explanation}</p>}<div className="mt-6 space-y-6">{quiz.questions.map((question, index) => <fieldset key={question.id} className="space-y-3"><legend className="text-sm font-medium leading-6 text-foreground">{index + 1}. {question.prompt}</legend>{question.options.map(option => <label key={option} className="flex cursor-pointer items-center gap-3 rounded-xl border border-line px-3 py-3 text-sm text-muted transition hover:bg-surface-hover has-[:checked]:border-primary has-[:checked]:bg-primary/5"><input type="radio" name={`question-${question.id}`} value={option} checked={answers[question.id] === option} onChange={event => setAnswers(current => ({ ...current, [question.id]: event.target.value }))} className="accent-indigo-500" />{option}</label>)}</fieldset>)}</div><button type="button" onClick={submit} disabled={busy || !quiz.questions.every(question => answers[question.id])} className="mt-7 inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">{busy ? t("submitting") : t("submitQuiz")}</button>{result && <p className="mt-4 text-sm text-primary" role="status">{t("latestResult")}: {result.score}/{result.total}</p>}{message && <p className="mt-4 text-sm text-amber-700 dark:text-amber-200" role="alert">{message}</p>}</section>;
}

export default function LessonPage({ params }: { params: Promise<{ slug: string; lessonSlug: string }> }) {
  const { locale, t, localized } = useI18n();
  const { slug, lessonSlug } = use(params);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [learning, setLearning] = useState<Learning | null>(null);
  const [completed, setCompleted] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);
  const [message, setMessage] = useState("");
  const [fontScale, setFontScale] = useState(1);
  const [focusMode, setFocusMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => { const storedScale = Number(window.localStorage.getItem("learn-coding-reading-font-scale")); if (storedScale >= 0.9 && storedScale <= 1.2) setFontScale(storedScale); setFocusMode(window.localStorage.getItem("learn-coding-reading-focus") === "true"); setSidebarCollapsed(window.localStorage.getItem("learn-coding-reading-sidebar") === "true"); }, []);
  useEffect(() => { window.localStorage.setItem("learn-coding-reading-font-scale", String(fontScale)); }, [fontScale]);
  useEffect(() => { window.localStorage.setItem("learn-coding-reading-focus", String(focusMode)); }, [focusMode]);
  useEffect(() => { window.localStorage.setItem("learn-coding-reading-sidebar", String(sidebarCollapsed)); }, [sidebarCollapsed]);
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      fetch(`/api/v1/courses/${encodeURIComponent(slug)}/lessons/${encodeURIComponent(lessonSlug)}`, { signal: controller.signal }).then(response => response.ok ? response.json() : Promise.reject(new Error("Lesson not found."))),
      fetch(`/api/v1/courses/${encodeURIComponent(slug)}/learning`, { signal: controller.signal }).then(response => response.ok ? response.json() : Promise.reject(new Error("Course not found."))),
      fetch(`/api/v1/me/courses/${encodeURIComponent(slug)}/progress`, { credentials: "include", signal: controller.signal }).then(response => response.ok ? response.json() : null),
    ]).then(([lessonValue, learningValue, progress]) => {
      setLesson(lessonValue);
      setLearning(learningValue);
      setProgressPercent(progress?.progress_percent ?? 0);
      setCompleted(Boolean(progress?.lessons?.find((item: { lesson_id: string; completed: boolean }) => item.lesson_id === lessonValue.id)?.completed));
      if (progress?.lessons?.some((item: { lesson_id: string }) => item.lesson_id === lessonValue.id)) fetch(`/api/v1/me/lessons/${lessonValue.id}/visit`, { method: "POST", credentials: "include", headers: { "X-CSRF-Token": csrf() } }).catch(() => undefined);
    }).catch(reason => { if (reason instanceof Error && reason.name === "AbortError") return; setMessage(reason instanceof Error ? reason.message : "Unable to load this lesson."); });
    return () => controller.abort();
  }, [slug, lessonSlug]);

  const orderedModules = useMemo(() => (learning?.modules ?? []).map(module => ({ ...module, lessons: [...module.lessons] })), [learning]);
  const flatLessons = useMemo(() => orderedModules.flatMap(module => module.lessons), [orderedModules]);
  const currentIndex = flatLessons.findIndex(item => item.slug === lessonSlug);
  const currentModuleIndex = orderedModules.findIndex(module => module.lessons.some(item => item.slug === lessonSlug));
  const previous = currentIndex > 0 ? flatLessons[currentIndex - 1] : null;
  const next = currentIndex >= 0 && currentIndex < flatLessons.length - 1 ? flatLessons[currentIndex + 1] : null;

  function toggleSidebar() { if (window.matchMedia("(min-width: 1024px)").matches) setSidebarCollapsed(value => !value); else setSidebarOpen(true); }

  async function markComplete() {
    if (!lesson) return;
    const response = await fetch(`/api/v1/me/lessons/${lesson.id}/progress`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() }, body: JSON.stringify({ completed: !completed }) });
    if (response.ok) {
      setCompleted(!completed);
      setMessage(!completed ? t("lessonMarked") : t("lessonReopened"));
      fetch(`/api/v1/me/courses/${encodeURIComponent(slug)}/progress`, { credentials: "include" }).then(result => result.ok ? result.json() : null).then(value => value && setProgressPercent(value.progress_percent ?? 0)).catch(() => undefined);
    } else if (response.status === 401) window.location.href = `/login?next=${encodeURIComponent(`/courses/${slug}/learn/${lessonSlug}`)}`;
    else setMessage((await response.json().catch(() => ({}))).detail ?? "Sign in and enroll to save progress.");
  }

  if (!lesson || !learning) return <section className="flex min-h-0 flex-1 items-center justify-center px-6 py-10"><p className="text-muted">{message || t("loading")}</p></section>;
  const lessonContent = localized(lesson.content_en, lesson.content_mm);

  return <section className="lesson-shell flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
    <div className="lesson-toolbar flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3 sm:px-6">
      <div className="flex min-w-0 items-center gap-2"><Link href={`/courses/${slug}`} className="inline-flex shrink-0 items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-primary transition hover:bg-surface-hover hover:text-foreground"><ArrowLeft size={16} /> <span className="hidden sm:inline">{t("backToCourse")}</span><span className="sm:hidden">{t("course")}</span></Link><button type="button" onClick={toggleSidebar} aria-label={t("curriculum")} aria-controls="lesson-curriculum" className="inline-flex items-center gap-2 rounded-lg border border-line bg-surface px-2.5 py-1.5 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><span className="hidden sm:inline">{t("curriculum")}</span>{sidebarCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}</button></div>
      <div className="flex items-center gap-1 rounded-xl border border-line bg-surface p-1" aria-label="Reading settings"><button type="button" aria-label="Decrease text size" onClick={() => setFontScale(value => Math.max(.9, Number((value - .1).toFixed(1))))} className="rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-foreground"><Minus size={15} /></button><span className="min-w-10 text-center text-xs text-muted">{Math.round(fontScale * 100)}%</span><button type="button" aria-label="Increase text size" onClick={() => setFontScale(value => Math.min(1.2, Number((value + .1).toFixed(1))))} className="rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-foreground"><Plus size={15} /></button><span className="mx-1 h-5 w-px bg-line" /><ThemeSwitcher /><button type="button" aria-pressed={focusMode} aria-label={focusMode ? "Exit focus mode" : "Enter focus mode"} onClick={() => setFocusMode(value => !value)} className={`rounded-lg p-2 transition ${focusMode ? "bg-primary/15 text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}><SunMoon size={16} /></button></div>
    </div>

    <div className="lesson-body grid min-h-0 min-w-0 flex-1 lg:grid-cols-[minmax(0,1fr)]"><div className={`${focusMode || sidebarCollapsed ? "lg:grid-cols-[minmax(0,1fr)]" : "lg:grid-cols-[310px_minmax(0,1fr)]"} lesson-workspace grid min-h-0 min-w-0 flex-1 overflow-hidden`}>
      <aside id="lesson-curriculum" className={`${sidebarOpen ? "fixed inset-y-0 left-0 z-50 block w-[min(86vw,320px)] shadow-2xl" : "hidden"} ${focusMode || sidebarCollapsed ? "lg:hidden" : "lg:block"} lesson-sidebar min-h-0 overflow-y-auto overscroll-contain border-r border-line bg-surface p-4`}><div className="flex items-start justify-between gap-3 border-b border-line pb-4"><div className="min-w-0"><p className="text-xs font-semibold uppercase tracking-[.16em] text-muted">{t("curriculum")}</p><p className="mt-2 break-words font-semibold text-foreground">{learning.title || t("courseLessons")}</p><div className="mt-4 h-1.5 overflow-hidden rounded-full bg-ink"><div className="h-full rounded-full bg-primary transition-[width]" style={{ width: `${progressPercent}%` }} /></div><p className="mt-2 text-xs text-muted">{Math.round(progressPercent)}% {t("complete")}</p></div><button type="button" aria-label={t("course")} onClick={() => setSidebarOpen(false)} className="shrink-0 rounded-lg p-2 text-muted hover:bg-surface-hover lg:hidden"><X size={17} /></button></div><nav className="mt-4 space-y-3" aria-label={t("curriculum")}>{orderedModules.map((module, moduleIndex) => <details key={module.id ?? module.title} open={moduleIndex === currentModuleIndex} className="group"><summary className="flex cursor-pointer list-none items-center justify-between gap-2 rounded-lg px-2 py-2 text-sm font-medium text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/60"><span className="break-words">{moduleIndex + 1}. {module.title}</span><ChevronDown size={15} className="shrink-0 text-muted transition group-open:rotate-180" /></summary><div className="mt-2 space-y-1 pl-1">{module.lessons.map(item => <Link key={item.id} href={`/courses/${slug}/learn/${item.slug}`} onClick={() => setSidebarOpen(false)} className={`flex items-start gap-2 rounded-xl px-2.5 py-2.5 text-sm transition ${item.slug === lessonSlug ? "bg-primary/12 font-medium text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}><span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-ink text-[10px]">{item.slug === lessonSlug ? <Check size={12} /> : ""}</span><span className="min-w-0 flex-1 whitespace-normal break-words leading-5">{item.title}</span><span className="shrink-0 text-[11px] text-muted">{item.duration_minutes ?? 0}m</span></Link>)}</div></details>)}</nav></aside>
      {sidebarOpen && <button type="button" aria-label="Close curriculum drawer" onClick={() => setSidebarOpen(false)} className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden" />}
      <div className="lesson-main min-h-0 min-w-0 overflow-y-auto overscroll-contain"><div className="mx-auto w-full max-w-[720px] px-4 py-6 sm:px-6 lg:py-8"><div className="flex items-start justify-between gap-4"><div className="min-w-0"><p className="text-xs font-semibold uppercase tracking-[.18em] text-primary">{t("lesson")} {currentIndex + 1} / {flatLessons.length}</p><h1 className="mt-2 break-words text-2xl font-semibold text-foreground sm:text-3xl">{lesson.title}</h1></div><span className="shrink-0 pt-1 text-sm text-muted">{lesson.duration_minutes ?? 0} min</span></div><div className="mt-4 h-1.5 overflow-hidden rounded-full bg-ink"><div className="h-full rounded-full bg-primary transition-[width]" style={{ width: `${progressPercent}%` }} /></div><article className="mt-8" style={{ fontSize: `${fontScale}em` }}>{locale === "my" && !lesson.content_mm?.trim() && <p className="mb-5 rounded-xl border border-amber-400/20 bg-amber-400/5 px-4 py-3 text-sm text-amber-200">{t("myanmarMissing")}</p>}{lesson.description && <p className="mb-8 text-lg leading-[1.8] text-muted">{lesson.description}</p>}<ContentBlocks content={lessonContent} />{lesson.code_examples?.length ? <div className="mt-10 space-y-6">{lesson.code_examples.map(example => <CodeExample key={example.id} example={example} />)}</div> : null}<LessonQuiz lessonId={lesson.id} /></article></div></div>
    </div></div>

    <footer className="lesson-footer shrink-0 border-t border-line bg-surface px-4 py-3 sm:px-6"><div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3"><Link href={previous ? `/courses/${slug}/learn/${previous.slug}` : `/courses/${slug}`} className="inline-flex items-center gap-2 rounded-xl border border-line px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><ArrowLeft size={16} /> <span className="hidden sm:inline">Previous lesson</span><span className="sm:hidden">Previous</span></Link><div className="order-3 flex min-w-[150px] flex-1 items-center gap-3 sm:order-2 sm:max-w-xs"><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-ink"><div className="h-full rounded-full bg-primary transition-[width]" style={{ width: `${progressPercent}%` }} /></div><span className="shrink-0 text-xs text-muted">{Math.round(progressPercent)}%</span></div><div className="order-2 flex items-center gap-2 sm:order-3"><button type="button" onClick={markComplete} className={`inline-flex items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-white transition ${completed ? "bg-emerald-600" : "bg-primary hover:bg-primary-hover"}`}>{completed ? <CheckCircle2 size={17} /> : <Check size={17} />}<span className="hidden sm:inline">{completed ? "Completed" : "Mark complete"}</span><span className="sm:hidden">{completed ? "Done" : "Complete"}</span></button><Link href={next ? `/courses/${slug}/learn/${next.slug}` : `/courses/${slug}`} className="inline-flex items-center gap-2 rounded-xl border border-line px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><span className="hidden sm:inline">{next ? "Next lesson" : "Finish course"}</span><span className="sm:hidden">{next ? "Next" : "Finish"}</span><ArrowRight size={16} /></Link></div></div>{message && <p className="mx-auto mt-2 max-w-6xl text-sm text-primary" role="status">{message}</p>}</footer>
  </section>;
}
