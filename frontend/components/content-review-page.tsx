"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Archive, BookOpen, Check, ChevronRight, Clock, Code2, Eye, FileText, RefreshCw, Search, Sparkles, Users, X } from "lucide-react";
import { contentReviewApi } from "@/lib/api";
import type { ContentReviewDashboard, ContentReviewDetail, ContentReviewEvent, ContentReviewItem, ContentReviewPerson } from "@/lib/types";

const contentTypes = [
  ["course", "Course"], ["module", "Module"], ["lesson", "Lesson"], ["syntax_reference", "Syntax reference"],
  ["challenge", "Coding challenge"], ["project", "Project"], ["career_path", "Career path"], ["public_page", "Public page"], ["legal_page", "Legal page"],
] as const;
const statuses = ["submitted", "in_review", "approved", "changes_requested", "rejected", "published"] as const;

function csrf() { return typeof document === "undefined" ? "" : document.cookie.split(";").map((value) => value.trim()).find((value) => value.startsWith("cm_csrf="))?.slice(8) ?? ""; }
function formatDate(value?: string | null) { return value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "—"; }
function label(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()); }
function personName(person?: ContentReviewPerson | null) { return person?.name || person?.email || "Unassigned"; }
function statusClass(status: string) {
  return status === "approved" || status === "published" ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-200" : status === "changes_requested" || status === "rejected" ? "border-rose-400/20 bg-rose-400/10 text-rose-200" : status === "in_review" ? "border-amber-400/20 bg-amber-400/10 text-amber-200" : "border-indigo-400/20 bg-indigo-400/10 text-indigo-200";
}

function PreviewValue({ value }: { value: unknown }) {
  if (value === null || value === undefined || value === "") return <span className="text-slate-500">—</span>;
  if (typeof value === "boolean" || typeof value === "number" || typeof value === "string") return <span className="whitespace-pre-wrap">{String(value)}</span>;
  return <pre className="max-h-52 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-black/20 p-3 text-xs leading-5 text-slate-300">{JSON.stringify(value, null, 2)}</pre>;
}

function Preview({ detail }: { detail: ContentReviewDetail }) {
  const preview = detail.preview;
  if (!preview) return <div className="rounded-2xl border border-line bg-surface/40 p-5 text-sm text-slate-400">The source content is no longer available.</div>;
  const entries = Object.entries(preview).filter(([key]) => !["title", "examples", "code_examples"].includes(key));
  const examples = (preview.examples || preview.code_examples) as unknown;
  return <div className="space-y-4">
    <div className="rounded-2xl border border-indigo-400/20 bg-indigo-500/10 p-5">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-indigo-300">Content preview</p>
      <h3 className="mt-2 text-lg font-semibold text-white">{String(preview.title || detail.title)}</h3>
      <p className="mt-1 text-xs text-slate-400">Version {detail.version} · {label(detail.content_type)}</p>
    </div>
    <div className="grid gap-3 sm:grid-cols-2">
      {entries.map(([key, value]) => <div key={key} className="rounded-xl border border-line bg-surface/50 p-4"><p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">{label(key)}</p><PreviewValue value={value}/></div>)}
    </div>
    {Array.isArray(examples) && examples.length > 0 && <div className="rounded-2xl border border-line bg-surface/60 p-4"><div className="flex items-center gap-2 text-sm font-semibold text-slate-200"><Code2 size={16} className="text-indigo-300"/> Code examples and expected output</div><div className="mt-4 space-y-4">{examples.map((example, index) => { const item = (typeof example === "object" && example !== null ? example : { code: example }) as Record<string, unknown>; return <div key={index} className="overflow-hidden rounded-xl border border-line bg-ink/50"><div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2 text-xs text-slate-400"><span>{String(item.title || `Example ${index + 1}`)}</span><span>{String(item.language || "code")}</span></div><pre className="overflow-auto p-4 text-xs leading-5 text-indigo-100">{String(item.code || "")}</pre>{item.expected_output !== undefined && <div className="border-t border-line bg-emerald-400/5 px-4 py-3"><p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-300">Expected output</p><pre className="mt-1 whitespace-pre-wrap text-xs leading-5 text-emerald-100">{String(item.expected_output || "")}</pre></div>}</div>; })}</div></div>}
  </div>;
}

function History({ events }: { events: ContentReviewEvent[] }) {
  return <div className="space-y-3">{events.length === 0 ? <p className="text-sm text-slate-500">No workflow events recorded.</p> : events.map((event) => <div key={event.id} className="flex gap-3"><div className="mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-indigo-500/15 text-indigo-300"><Activity size={14}/></div><div className="min-w-0"><p className="text-sm text-slate-200"><span className="font-semibold">{personName(event.actor)}</span> moved this item {event.from_status ? <><span className="text-slate-400">from {label(event.from_status)} to </span></> : "to "}<span className="font-semibold text-indigo-200">{label(event.to_status)}</span></p><p className="mt-1 text-xs text-slate-500">{formatDate(event.created_at)}</p>{event.comment && <p className="mt-2 rounded-lg bg-surface p-3 text-sm leading-6 text-slate-300">{event.comment}</p>}</div></div>)}</div>;
}

export default function ContentReviewPage() {
  const [dashboard, setDashboard] = useState<ContentReviewDashboard | null>(null);
  const [queue, setQueue] = useState<{ items: ContentReviewItem[]; page: number; page_size: number; total: number; pages: number }>({ items: [], page: 1, page_size: 25, total: 0, pages: 0 });
  const [reviewers, setReviewers] = useState<ContentReviewPerson[]>([]);
  const [authors, setAuthors] = useState<ContentReviewPerson[]>([]);
  const [detail, setDetail] = useState<ContentReviewDetail | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [queueLoading, setQueueLoading] = useState(false);
  const [tab, setTab] = useState<"all" | "mine" | "attention">("all");
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ search: "", status: "", content_type: "", author_id: "", date_from: "", date_to: "" });
  const [theme, setTheme] = useState<"system" | "dark" | "light">("system");
  const [submitForm, setSubmitForm] = useState({ content_type: "course", content_key: "" });
  const [decisionComment, setDecisionComment] = useState("");
  const [comment, setComment] = useState("");
  const [commentType, setCommentType] = useState("general");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [systemLight, setSystemLight] = useState(false);

  const themeIsLight = theme === "light" || (theme === "system" && systemLight);
  const surface = themeIsLight ? "bg-white text-slate-900" : "bg-ink text-slate-100";
  const panel = themeIsLight ? "border-slate-200 bg-white" : "border-line bg-surface";
  const muted = themeIsLight ? "text-slate-500" : "text-slate-400";
  const control = themeIsLight ? "border-slate-200 bg-slate-50 text-slate-800" : "border-line bg-surface text-slate-200";

  const loadQueue = useCallback(() => {
    setQueueLoading(true);
    const params = new URLSearchParams();
    if (filters.search.trim()) params.set("search", filters.search.trim());
    if (filters.status) params.set("status", filters.status);
    if (filters.content_type) params.set("content_type", filters.content_type);
    if (filters.author_id) params.set("author_id", filters.author_id);
    if (filters.date_from) params.set("date_from", `${filters.date_from}T00:00:00Z`);
    if (filters.date_to) params.set("date_to", `${filters.date_to}T23:59:59Z`);
    if (tab === "mine") params.set("mine", "true");
    if (tab === "attention") params.set("needs_attention", "true");
    params.set("page", String(page)); params.set("page_size", "12");
    contentReviewApi.queue(`?${params.toString()}`).then((data) => { setQueue(data); setSelectedId((current) => data.items.some((item) => item.id === current) ? current : data.items[0]?.id || ""); }).catch((e: Error) => setError(e.message)).finally(() => setQueueLoading(false));
  }, [filters.author_id, filters.content_type, filters.date_from, filters.date_to, filters.search, filters.status, page, tab]);

  useEffect(() => {
    Promise.all([contentReviewApi.dashboard(), contentReviewApi.reviewers(), contentReviewApi.authors()]).then(([nextDashboard, nextReviewers, nextAuthors]) => { setDashboard(nextDashboard); setReviewers(nextReviewers); setAuthors(nextAuthors); }).catch((e: Error) => setError(e.message)).finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: light)");
    const update = () => setSystemLight(media.matches);
    update(); media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => { loadQueue(); }, [loadQueue]);
  useEffect(() => { if (!selectedId) { setDetail(null); return; } contentReviewApi.detail(selectedId).then(setDetail).catch((e: Error) => setError(e.message)); }, [selectedId]);

  const updateFilter = (key: keyof typeof filters, value: string) => { setPage(1); setFilters((current) => ({ ...current, [key]: value })); };
  const refresh = () => { setError(""); setLoading(true); Promise.all([contentReviewApi.dashboard(), contentReviewApi.reviewers(), contentReviewApi.authors()]).then(([nextDashboard, nextReviewers, nextAuthors]) => { setDashboard(nextDashboard); setReviewers(nextReviewers); setAuthors(nextAuthors); }).catch((e: Error) => setError(e.message)).finally(() => setLoading(false)); loadQueue(); if (selectedId) contentReviewApi.detail(selectedId).then(setDetail).catch((e: Error) => setError(e.message)); };
  const runAction = async (action: () => Promise<unknown>, success: string) => { setBusy(true); setError(""); setMessage(""); try { await action(); setMessage(success); refresh(); if (selectedId) setDetail(await contentReviewApi.detail(selectedId)); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } };
  const submit = (event: { preventDefault: () => void }) => { event.preventDefault(); if (!submitForm.content_key.trim()) return; runAction(() => contentReviewApi.submit({ ...submitForm, content_key: submitForm.content_key.trim() }, csrf()), "Submitted to the review queue.").then(() => setSubmitForm((current) => ({ ...current, content_key: "" }))); };

  return <div className={`min-h-[calc(100vh-72px)] rounded-3xl p-1 transition-colors ${surface}`}>
    <div className="px-1 py-2 sm:px-3 lg:px-5">
      <div className="flex flex-col gap-5 border-b border-current/10 pb-7 xl:flex-row xl:items-end xl:justify-between">
        <div><div className="flex items-center gap-2 text-sm font-semibold text-indigo-400"><Sparkles size={16}/> Platform governance</div><h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">Content Review</h1><p className={`mt-2 max-w-2xl text-sm leading-6 ${muted}`}>Review submitted learning content in one platform queue. Organization selection is not required for this global admin workspace.</p></div>
        <div className="flex flex-wrap items-center gap-2"><div className={`flex rounded-xl border p-1 ${panel}`} aria-label="Theme"><button onClick={() => setTheme("system")} className={`rounded-lg px-2.5 py-1.5 text-xs ${theme === "system" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>System</button><button onClick={() => setTheme("dark")} className={`rounded-lg px-2.5 py-1.5 text-xs ${theme === "dark" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>Dark</button><button onClick={() => setTheme("light")} className={`rounded-lg px-2.5 py-1.5 text-xs ${theme === "light" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>Light</button></div><button onClick={refresh} className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm ${panel} ${muted}`}><RefreshCw size={15}/> Refresh</button></div>
      </div>

      {error && <div role="alert" className="mt-5 flex items-start justify-between gap-3 rounded-xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200"><span>{error}</span><button onClick={() => setError("")} aria-label="Dismiss error"><X size={16}/></button></div>}
      {message && <div role="status" className="mt-5 rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">{message}</div>}

      <div className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">{[
        ["Pending review", dashboard?.pending_review ?? 0, "Needs a first review", "text-indigo-300"], ["In review", dashboard?.in_review ?? 0, "Currently assigned", "text-amber-300"], ["Approved", dashboard?.approved ?? 0, "Ready to publish", "text-emerald-300"], ["Changes requested", dashboard?.changes_requested ?? 0, "Waiting on author", "text-rose-300"], ["Rejected", dashboard?.rejected ?? 0, "Returned with reason", "text-slate-300"],
      ].map(([name, value, hint, color]) => <div key={String(name)} className={`rounded-2xl border p-4 ${panel}`}><p className={`text-xs ${muted}`}>{name}</p><p className={`mt-2 text-3xl font-bold ${color}`}>{loading ? "—" : value}</p><p className={`mt-1 text-xs ${muted}`}>{hint}</p></div>)}</div>

      <div className="mt-7 grid items-start gap-4 xl:max-h-[calc(100vh-250px)] xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,.75fr)] xl:overflow-y-auto">
        <section className={`min-w-0 rounded-2xl border p-4 sm:p-5 ${panel}`}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"><div><p className="text-sm font-semibold">Review queue</p><p className={`mt-1 text-xs ${muted}`}>{queue.total} total records · server-side filters and pagination</p></div><div className={`flex rounded-xl border p-1 ${themeIsLight ? "border-slate-200" : "border-line"}`}><button onClick={() => { setTab("all"); setPage(1); }} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${tab === "all" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>All reviews</button><button onClick={() => { setTab("mine"); setPage(1); }} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${tab === "mine" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>My reviews</button><button onClick={() => { setTab("attention"); setPage(1); }} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${tab === "attention" ? "bg-indigo-500/20 text-indigo-300" : muted}`}>Needs attention</button></div></div>
          <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3"><label className={`flex items-center gap-2 rounded-xl border px-3 py-2 ${control} lg:col-span-2`}><Search size={16} className={muted}/><input aria-label="Search content reviews" value={filters.search} onChange={(event) => updateFilter("search", event.target.value)} placeholder="Search title…" className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-500"/></label><select aria-label="Review status" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)} className={`rounded-xl border px-3 py-2 text-sm outline-none ${control}`}><option value="">All statuses</option>{statuses.map((status) => <option key={status} value={status}>{label(status)}</option>)}</select><select aria-label="Content type" value={filters.content_type} onChange={(event) => updateFilter("content_type", event.target.value)} className={`rounded-xl border px-3 py-2 text-sm outline-none ${control}`}><option value="">All content types</option>{contentTypes.map(([value, name]) => <option key={value} value={value}>{name}</option>)}</select><select aria-label="Author" value={filters.author_id} onChange={(event) => updateFilter("author_id", event.target.value)} className={`rounded-xl border px-3 py-2 text-sm outline-none ${control}`}><option value="">All authors</option>{authors.map((author) => <option key={author.id} value={author.id}>{personName(author)}</option>)}</select><div className="grid grid-cols-2 gap-2"><input aria-label="Submitted from" type="date" value={filters.date_from} onChange={(event) => updateFilter("date_from", event.target.value)} className={`min-w-0 rounded-xl border px-3 py-2 text-xs outline-none ${control}`}/><input aria-label="Submitted to" type="date" value={filters.date_to} onChange={(event) => updateFilter("date_to", event.target.value)} className={`min-w-0 rounded-xl border px-3 py-2 text-xs outline-none ${control}`}/></div></div>
          <div className="mt-5 overflow-x-auto rounded-xl border border-current/10"><table className="w-full min-w-[860px] border-collapse text-left"><thead><tr className={`text-[11px] uppercase tracking-wider ${muted}`}><th className="px-4 py-3 font-semibold">Content</th><th className="px-4 py-3 font-semibold">Type / scope</th><th className="px-4 py-3 font-semibold">Submitted by</th><th className="px-4 py-3 font-semibold">Submitted</th><th className="px-4 py-3 font-semibold">Reviewer</th><th className="px-4 py-3 font-semibold">Status</th><th className="px-4 py-3"/></tr></thead><tbody>{queueLoading ? <tr><td colSpan={7} className={`px-4 py-12 text-center text-sm ${muted}`}>Loading review records…</td></tr> : queue.items.length === 0 ? <tr><td colSpan={7} className={`px-4 py-12 text-center text-sm ${muted}`}><Archive className="mx-auto mb-3 opacity-50" size={24}/>No review records match these filters.</td></tr> : queue.items.map((item) => <tr key={item.id} onClick={() => setSelectedId(item.id)} className={`cursor-pointer border-t border-current/10 transition hover:bg-indigo-500/5 ${selectedId === item.id ? "bg-indigo-500/10" : ""}`}><td className="max-w-[300px] px-4 py-4"><p className="truncate text-sm font-semibold">{item.title}</p><p className={`mt-1 text-xs ${muted}`}>v{item.version} · {item.content_key}</p></td><td className="px-4 py-4"><p className="text-xs font-medium">{label(item.content_type)}</p><p className={`mt-1 text-xs ${muted}`}>{item.organization?.name || "Platform"}</p></td><td className={`px-4 py-4 text-xs ${muted}`}>{personName(item.submitted_by)}</td><td className={`whitespace-nowrap px-4 py-4 text-xs ${muted}`}>{formatDate(item.submitted_at)}</td><td className={`px-4 py-4 text-xs ${muted}`}>{personName(item.reviewer)}</td><td className="px-4 py-4"><span className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[11px] font-semibold ${statusClass(item.status)}`}>{label(item.status)}</span></td><td className="px-4 py-4 text-indigo-300"><ChevronRight size={16}/></td></tr>)}</tbody></table></div>
          <div className="mt-4 flex items-center justify-between gap-3"><p className={`text-xs ${muted}`}>Showing {queue.items.length ? (queue.page - 1) * queue.page_size + 1 : 0}–{Math.min(queue.page * queue.page_size, queue.total)} of {queue.total}</p><div className="flex gap-2"><button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className={`rounded-lg border px-3 py-1.5 text-xs disabled:opacity-40 ${panel}`}>Previous</button><span className={`px-2 py-1.5 text-xs ${muted}`}>{queue.page} / {Math.max(queue.pages, 1)}</span><button disabled={page >= queue.pages} onClick={() => setPage((value) => value + 1)} className={`rounded-lg border px-3 py-1.5 text-xs disabled:opacity-40 ${panel}`}>Next</button></div></div>
        </section>

        <aside className="space-y-4">
          <form onSubmit={submit} className={`rounded-2xl border p-5 ${panel}`}><div className="flex items-center gap-2 text-sm font-semibold"><FileText size={16} className="text-indigo-300"/> Submit a version</div><p className={`mt-2 text-xs leading-5 ${muted}`}>Reference an existing content record by UUID. The API validates the record and prevents duplicate active reviews.</p><div className="mt-4 grid gap-2"><select aria-label="Submission content type" value={submitForm.content_type} onChange={(event) => setSubmitForm((current) => ({ ...current, content_type: event.target.value }))} className={`rounded-xl border px-3 py-2 text-sm outline-none ${control}`}>{contentTypes.map(([value, name]) => <option key={value} value={value}>{name}</option>)}</select><input aria-label="Content key" required value={submitForm.content_key} onChange={(event) => setSubmitForm((current) => ({ ...current, content_key: event.target.value }))} placeholder="Content ID or public page slug" className={`rounded-xl border px-3 py-2 text-sm outline-none ${control}`}/><button disabled={busy} className="mt-1 rounded-xl bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:opacity-50">Submit for review</button></div></form>
          <div className={`rounded-2xl border p-5 ${panel}`}><div className="flex items-center justify-between"><div className="flex items-center gap-2 text-sm font-semibold"><Eye size={16} className="text-indigo-300"/> Review detail</div>{detail && <span className={`rounded-full border px-2 py-1 text-[10px] font-semibold ${statusClass(detail.status)}`}>{label(detail.status)}</span>}</div>{!detail ? <div className={`py-12 text-center text-sm ${muted}`}><BookOpen className="mx-auto mb-3 opacity-50" size={25}/>Select a record to inspect its content.</div> : <div className="mt-4 space-y-5"><div><h2 className="text-lg font-semibold">{detail.title}</h2><p className={`mt-1 text-xs ${muted}`}>{label(detail.content_type)} · version {detail.version} · {detail.organization?.name || "Platform"}</p></div><div className="flex flex-wrap gap-2">{detail.status === "submitted" && <button disabled={busy} onClick={() => runAction(() => contentReviewApi.transition(detail.id, { status: "in_review" }, csrf()), "Review started.")} className="rounded-lg bg-amber-500/15 px-3 py-2 text-xs font-semibold text-amber-200">Start review</button>}{detail.status === "in_review" && <><button disabled={busy} onClick={() => runAction(() => contentReviewApi.transition(detail.id, { status: "approved" }, csrf()), "Review approved. Publishing remains a separate action.")} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/15 px-3 py-2 text-xs font-semibold text-emerald-200"><Check size={14}/> Approve</button><button disabled={busy || !decisionComment.trim()} onClick={() => runAction(() => contentReviewApi.transition(detail.id, { status: "changes_requested", comment: decisionComment }, csrf()), "Changes requested.")} className="rounded-lg bg-rose-500/15 px-3 py-2 text-xs font-semibold text-rose-200">Request changes</button><button disabled={busy || !decisionComment.trim()} onClick={() => runAction(() => contentReviewApi.transition(detail.id, { status: "rejected", comment: decisionComment }, csrf()), "Review rejected with a recorded reason.")} className="rounded-lg bg-rose-500/15 px-3 py-2 text-xs font-semibold text-rose-200">Reject</button></>}{detail.status === "approved" && <button disabled={busy} onClick={() => runAction(() => contentReviewApi.publish(detail.id, csrf()), "Published after explicit approval.")} className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-semibold text-white">Publish</button>}</div>{detail.status === "in_review" && <textarea aria-label="Decision comment" value={decisionComment} onChange={(event) => setDecisionComment(event.target.value)} placeholder="Required for changes requested or rejected…" className={`min-h-20 w-full rounded-xl border px-3 py-2 text-sm outline-none ${control}`}/>}<Preview detail={detail}/><div className="border-t border-current/10 pt-5"><div className="flex items-center gap-2 text-sm font-semibold"><Users size={16} className="text-indigo-300"/> Assignment</div><select aria-label="Assign reviewer" value={detail.reviewer?.id || ""} onChange={(event) => runAction(() => contentReviewApi.assign(detail.id, event.target.value, csrf()), "Reviewer assignment updated.")} className={`mt-3 w-full rounded-xl border px-3 py-2 text-sm outline-none ${control}`}><option value="">Assign a reviewer…</option>{reviewers.map((reviewer) => <option key={reviewer.id} value={reviewer.id}>{personName(reviewer)} · {label(reviewer.role)}</option>)}</select></div><div className="border-t border-current/10 pt-5"><div className="flex items-center gap-2 text-sm font-semibold"><Sparkles size={16} className="text-indigo-300"/> Discussion</div><div className="mt-3 space-y-3">{detail.comments.length === 0 ? <p className={`text-xs ${muted}`}>No comments yet.</p> : detail.comments.map((item) => <div key={item.id} className="rounded-xl bg-black/10 p-3"><div className="flex justify-between gap-3 text-xs"><span className="font-semibold">{personName(item.author)}</span><span className={muted}>v{item.review_version} · {formatDate(item.created_at)}</span></div><p className="mt-2 whitespace-pre-wrap text-sm leading-6">{item.body}</p></div>)}</div><div className="mt-3 grid gap-2"><div className="flex gap-2"><select aria-label="Comment type" value={commentType} onChange={(event) => setCommentType(event.target.value)} className={`rounded-xl border px-3 py-2 text-xs outline-none ${control}`}><option value="general">General</option><option value="correction">Correction</option><option value="code_quality">Code quality</option><option value="accuracy">Accuracy</option><option value="accessibility">Accessibility</option></select><button disabled={busy || !comment.trim()} onClick={() => runAction(() => contentReviewApi.comment(detail.id, { comment_type: commentType, body: comment }, csrf()), "Comment added.")} className="rounded-xl bg-surface px-3 py-2 text-xs font-semibold text-indigo-200 disabled:opacity-40">Add comment</button></div><textarea aria-label="Review comment" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Leave a versioned review note…" className={`min-h-20 w-full rounded-xl border px-3 py-2 text-sm outline-none ${control}`}/></div></div><div className="border-t border-current/10 pt-5"><div className="mb-3 flex items-center gap-2 text-sm font-semibold"><Clock size={16} className="text-indigo-300"/> Workflow history</div><History events={detail.history}/></div></div>}</div>
        </aside>
      </div>
      <p className={`mt-5 flex items-center gap-2 text-xs ${muted}`}><Users size={14}/> {dashboard?.total ?? 0} records are governed by server-side RBAC, tenant-safe organization fields, versioned comments, audit events, and explicit publication.</p>
    </div>
  </div>;
}
