"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronRight, Download, FileText, Plus, RefreshCw, Search, Tags, Trash2 } from "lucide-react";
import { ApiError, notesApi } from "@/lib/api";
import type { NotebookFolder, NotebookTag, PersonalNote } from "@/lib/types";
import { csrf } from "@/components/auth-form";

type Draft = {
  id?: string;
  title: string;
  content: string;
  course_id: string;
  lesson_id: string;
  folder_id: string;
  tags: string[];
  is_favorite: boolean;
  is_pinned: boolean;
  version: number;
};
type SaveState = "idle" | "saving" | "saved" | "error" | "conflict";

const emptyDraft = (courseId = "", lessonId = ""): Draft => ({ id: undefined, title: "", content: "", course_id: courseId, lesson_id: lessonId, folder_id: "", tags: [], is_favorite: false, is_pinned: false, version: 1 });
const draftFromNote = (note: PersonalNote): Draft => ({ id: note.id, title: note.title, content: note.content ?? "", course_id: note.course?.id ?? "", lesson_id: note.lesson?.id ?? "", folder_id: note.folder?.id ?? "", tags: note.tags.map(tag => tag.name), is_favorite: note.is_favorite, is_pinned: note.is_pinned, version: note.version });

function MarkdownPreview({ value }: { value: string }) {
  return <div className="prose prose-invert max-w-none whitespace-pre-wrap text-sm leading-7 text-slate-300">{value || <span className="text-slate-600">Preview will appear here.</span>}</div>;
}

function Toolbar({ onInsert, onHistory = action => { document.execCommand(action); } }: { onInsert: (value: string, selectLength?: number) => void; onHistory?: (action: "undo" | "redo") => void }) {
  const buttons: [string, string, number?][] = [["H1", "# "], ["H2", "## "], ["B", "**text**", 4], ["I", "*text*", 4], ["• list", "- "], ["1. list", "1. "], ["link", "[text](url)", 4], ["code", "`code`", 4], ["```", "```\ncode\n```", 4]];
  return <div className="flex flex-wrap gap-1 border-b border-line px-2 py-2" aria-label="Markdown formatting toolbar"><button type="button" onClick={() => onHistory("undo")} className="rounded-lg border border-line bg-surface px-2.5 py-1.5 text-xs font-semibold text-slate-300 hover:border-indigo-400 hover:text-white" aria-label="Undo">↶</button><button type="button" onClick={() => onHistory("redo")} className="rounded-lg border border-line bg-surface px-2.5 py-1.5 text-xs font-semibold text-slate-300 hover:border-indigo-400 hover:text-white" aria-label="Redo">↷</button>{buttons.map(([label, value, selectLength]) => <button key={label} type="button" onClick={() => onInsert(value, selectLength)} className="rounded-lg border border-line bg-surface px-2.5 py-1.5 text-xs font-semibold text-slate-300 hover:border-indigo-400 hover:text-white">{label}</button>)}</div>;
}

export default function NotebookPage() {
  const [notes, setNotes] = useState<PersonalNote[]>([]);
  const [folders, setFolders] = useState<NotebookFolder[]>([]);
  const [tags, setTags] = useState<NotebookTag[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [search, setSearch] = useState("");
  const [view, setView] = useState("all");
  const [folderId, setFolderId] = useState("");
  const [tag, setTag] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dirty, setDirty] = useState(false);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [saveError, setSaveError] = useState("");
  const [preview, setPreview] = useState(false);
  const [context, setContext] = useState({ courseId: "", lessonId: "", courseSlug: "", lessonSlug: "" });
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const draftRef = useRef<Draft | null>(null);
  const dirtyRef = useRef(false);
  const revisionRef = useRef(0);
  const savingRef = useRef(false);
  const queuedRef = useRef(false);

  const loadNotes = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ view, page: String(page), page_size: "12", sort: "updated_at", order: "desc" });
      if (search.trim()) params.set("search", search.trim());
      if (folderId) params.set("folder_id", folderId);
      if (tag) params.set("tag", tag);
      const result = await notesApi.list(`?${params.toString()}`);
      setNotes(result.items); setPages(result.pages); setTotal(result.total);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load your notes.");
    } finally { setLoading(false); }
  }, [folderId, page, search, tag, view]);

  const loadMeta = useCallback(async () => {
    const [folderResult, tagResult] = await Promise.allSettled([notesApi.folders(), notesApi.tags()]);
    if (folderResult.status === "fulfilled") setFolders(folderResult.value);
    if (tagResult.status === "fulfilled") setTags(tagResult.value);
  }, []);

  useEffect(() => { void loadMeta(); }, [loadMeta]);
  useEffect(() => { void loadNotes(); }, [loadNotes]);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initial = { courseId: params.get("course_id") ?? "", lessonId: params.get("lesson_id") ?? "", courseSlug: params.get("course_slug") ?? "", lessonSlug: params.get("lesson_slug") ?? "" };
    setContext(initial);
    const noteId = params.get("note");
    if (noteId) setSelectedId(noteId);
    else if (params.get("new")) loadDraft(emptyDraft(initial.courseId, initial.lessonId));
  }, []);

  function loadDraft(next: Draft) {
    draftRef.current = next; revisionRef.current += 1; dirtyRef.current = false; setDirty(false); setDraft(next); setSaveState("idle"); setSaveError("");
  }

  useEffect(() => {
    if (!selectedId) return;
    let active = true;
    notesApi.detail(selectedId).then(note => { if (active) loadDraft(draftFromNote(note)); }).catch(value => { if (active) setError(value instanceof Error ? value.message : "Unable to open this note."); });
    return () => { active = false; };
  }, [selectedId]);

  const updateDraft = (patch: Partial<Draft>) => {
    setDraft(previous => {
      if (!previous) return previous;
      const next = { ...previous, ...patch };
      draftRef.current = next; revisionRef.current += 1; dirtyRef.current = true;
      return next;
    });
    setDirty(true); setSaveState("idle"); setSaveError("");
  };

  const saveNow = useCallback(async () => {
    const current = draftRef.current;
    if (!current || (!current.title.trim() && !current.content.trim())) return;
    if (savingRef.current) { queuedRef.current = true; return; }
    savingRef.current = true;
    const revision = revisionRef.current;
    setSaveState("saving"); setSaveError("");
    try {
      const body = { title: current.title, content: current.content, course_id: current.course_id || null, lesson_id: current.lesson_id || null, folder_id: current.folder_id || null, tags: current.tags, is_favorite: current.is_favorite, is_pinned: current.is_pinned, version: current.version };
      const saved = current.id ? await notesApi.update(current.id, body, csrf()) : await notesApi.create(body, csrf());
      const changedWhileSaving = revisionRef.current !== revision;
      const next = { ...draftRef.current ?? current, id: saved.id, version: saved.version };
      draftRef.current = next; setDraft(next);
      if (changedWhileSaving) { dirtyRef.current = true; setDirty(true); queuedRef.current = true; } else { dirtyRef.current = false; setDirty(false); setSaveState("saved"); }
      void loadNotes(); void loadMeta();
    } catch (value) {
      if (value instanceof ApiError && value.status === 409) { setSaveState("conflict"); setSaveError(value.message); }
      else { setSaveState("error"); setSaveError(value instanceof Error ? value.message : "Save failed. Your draft is still here."); }
    } finally {
      savingRef.current = false;
      if (queuedRef.current) { queuedRef.current = false; window.setTimeout(() => void saveNow(), 0); }
    }
  }, [loadMeta, loadNotes]);

  useEffect(() => {
    if (!dirty || !draft) return;
    const timer = window.setTimeout(() => void saveNow(), 750);
    return () => window.clearTimeout(timer);
  }, [dirty, draft, saveNow]);

  useEffect(() => {
    const guard = (event: BeforeUnloadEvent) => { if (dirtyRef.current) { event.preventDefault(); event.returnValue = ""; } };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, []);

  function selectNote(id: string) {
    if (dirty && !window.confirm("Discard unsaved changes?")) return;
    setSelectedId(id); setDraft(null); setPreview(false);
  }
  function newNote() {
    if (dirty && !window.confirm("Discard unsaved changes?")) return;
    setSelectedId(null); loadDraft(emptyDraft(context.courseId, context.lessonId)); setPreview(false);
  }
  function insertMarkdown(value: string, selectLength = 0) {
    const textarea = textareaRef.current;
    if (!textarea || !draft) return;
    const start = textarea.selectionStart; const end = textarea.selectionEnd; const selected = draft.content.slice(start, end);
    const output = selected ? value.replace("text", selected).replace("code", selected) : value;
    updateDraft({ content: draft.content.slice(0, start) + output + draft.content.slice(end) });
    window.requestAnimationFrame(() => { textarea.focus(); textarea.setSelectionRange(start + (selected ? output.length : 0), start + (selected ? output.length : selectLength)); });
  }
  async function removeNote() {
    if (!draft?.id || !window.confirm("Delete this private note permanently?")) return;
    try { await notesApi.remove(draft.id, csrf()); setSelectedId(null); loadDraft(emptyDraft(context.courseId, context.lessonId)); await loadNotes(); }
    catch (value) { setSaveState("error"); setSaveError(value instanceof Error ? value.message : "Unable to delete note."); }
  }
  async function exportNote() {
    if (!draft?.id) return;
    const result = await notesApi.export(draft.id); const blob = new Blob([result.content], { type: "text/markdown" }); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = result.filename; anchor.click(); URL.revokeObjectURL(url);
  }
  async function createFolder() {
    const name = window.prompt("Folder name");
    if (!name?.trim()) return;
    try { await notesApi.createFolder({ name: name.trim() }, csrf()); await loadMeta(); }
    catch (value) { setError(value instanceof Error ? value.message : "Unable to create folder."); }
  }

  const statusLabel = saveState === "saving" ? "Saving…" : saveState === "saved" ? "Saved" : saveState === "conflict" ? "Conflict — local draft kept" : saveState === "error" ? "Save failed" : dirty ? "Unsaved changes" : "";
  return <div className="mx-auto max-w-[1500px]">
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-semibold text-indigo-300">Private learning workspace</p><h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">My notebook</h1><p className="mt-2 text-sm text-slate-400">Capture ideas, code snippets, and course notes in one place.</p></div><button type="button" onClick={newNote} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"><Plus size={16} /> New note</button></div>
    <div className="mb-3 flex justify-end"><button type="button" onClick={() => void createFolder()} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-400 hover:border-indigo-400 hover:text-white">+ New folder</button></div>
    <div className="grid min-h-[620px] gap-4 xl:grid-cols-[220px_330px_minmax(0,1fr)]">
      <aside className="rounded-2xl border border-line bg-surface/70 p-3"><p className="px-3 py-2 text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">Notebook</p>{[["all", "All notes"], ["course", "Course notes"], ["personal", "Personal"], ["favorites", "Favorites"], ["pinned", "Pinned"]].map(([value, label]) => <button key={value} type="button" onClick={() => { setView(value); setPage(1); }} className={`mb-1 flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm ${view === value ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:bg-white/[.05] hover:text-white"}`}>{label}<span className="text-xs text-slate-600">{value === "all" ? total : ""}</span></button>)}<div className="my-4 border-t border-line" /><p className="flex items-center gap-2 px-3 py-2 text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">▦ Folders</p>{folders.length ? folders.map(folder => <button key={folder.id} type="button" onClick={() => { setFolderId(folder.id); setPage(1); }} className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm ${folderId === folder.id ? "bg-indigo-500/15 text-indigo-200" : "text-slate-400 hover:bg-white/[.05] hover:text-white"}`}><span className="truncate">{folder.name}</span><span className="text-xs text-slate-600">{folder.note_count}</span></button>) : <p className="px-3 text-xs text-slate-600">Folders appear as you create them.</p>}<div className="my-4 border-t border-line" /><p className="flex items-center gap-2 px-3 py-2 text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500"><Tags size={13} /> Tags</p>{tags.length ? <div className="flex flex-wrap gap-1 px-2">{tags.map(item => <button key={item.id} type="button" onClick={() => { setTag(item.name); setPage(1); }} className={`rounded-full px-2 py-1 text-[11px] ${tag === item.name ? "bg-indigo-500/25 text-indigo-200" : "bg-elevated text-slate-400 hover:text-white"}`}>#{item.name}</button>)}</div> : <p className="px-3 text-xs text-slate-600">Tags appear on saved notes.</p>}<button type="button" onClick={() => { setFolderId(""); setTag(""); setPage(1); }} className="mt-5 w-full rounded-lg px-3 py-2 text-left text-xs text-slate-500 hover:bg-white/[.05] hover:text-white">Clear folder/tag filters</button></aside>
      <section className="min-w-0 rounded-2xl border border-line bg-surface/50 p-3"><div className="relative"><Search className="absolute left-3 top-3 text-slate-500" size={16} /><input value={search} onChange={event => { setSearch(event.target.value); setPage(1); }} placeholder="Search title or content…" className="w-full rounded-xl border border-line bg-ink/60 py-2.5 pl-9 pr-3 text-sm text-slate-200 placeholder:text-slate-600 focus:border-indigo-400 focus:outline-none" /></div><div className="mt-3 flex items-center justify-between px-1 text-xs text-slate-500"><span>{loading ? "Loading…" : `${total} note${total === 1 ? "" : "s"}`}</span><button type="button" onClick={() => void loadNotes()} aria-label="Refresh notes" className="rounded-lg p-1.5 hover:bg-elevated hover:text-white"><RefreshCw size={14} /></button></div>{error && <p className="mt-3 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-xs text-red-200">{error}</p>}<div className="mt-3 space-y-2">{!loading && !notes.length && <div className="rounded-xl border border-dashed border-line p-6 text-center"><FileText className="mx-auto text-slate-600" size={24} /><p className="mt-3 text-sm text-slate-400">No notes match these filters.</p><button type="button" onClick={newNote} className="mt-3 text-xs font-semibold text-indigo-300 hover:text-white">Create a note →</button></div>}{notes.map(note => <button key={note.id} type="button" onClick={() => selectNote(note.id)} className={`w-full rounded-xl border p-3 text-left transition ${selectedId === note.id ? "border-indigo-400/70 bg-indigo-500/10" : "border-line bg-ink/30 hover:border-indigo-400/40"}`}><div className="flex items-start justify-between gap-2"><span className="line-clamp-2 text-sm font-semibold text-slate-100">{note.title || "Untitled note"}</span><span className="shrink-0 text-[10px] text-slate-600">{new Date(note.updated_at).toLocaleDateString()}</span></div><p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">{note.excerpt || "Empty note"}</p><div className="mt-2 flex flex-wrap gap-1">{note.is_pinned && <span className="rounded-full bg-indigo-500/15 px-2 py-0.5 text-[10px] text-indigo-200">Pinned</span>}{note.is_favorite && <span className="rounded-full bg-amber-400/10 px-2 py-0.5 text-[10px] text-amber-200">Favorite</span>}{note.tags.slice(0, 2).map(item => <span key={item.id} className="rounded-full bg-elevated px-2 py-0.5 text-[10px] text-slate-400">#{item.name}</span>)}</div></button>)}</div><div className="mt-4 flex items-center justify-between border-t border-line pt-3 text-xs text-slate-500"><span>Page {page} of {Math.max(1, pages)}</span><div className="flex gap-1"><button type="button" disabled={page <= 1} onClick={() => setPage(value => value - 1)} className="rounded-lg border border-line p-1.5 disabled:opacity-30">←</button><button type="button" disabled={page >= pages} onClick={() => setPage(value => value + 1)} className="rounded-lg border border-line p-1.5 disabled:opacity-30"><ChevronRight size={15} /></button></div></div></section>
      <section className="min-w-0 rounded-2xl border border-line bg-surface/70 p-4 sm:p-6">{draft ? <><div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4"><div className="flex min-w-0 items-center gap-2 text-xs text-slate-500"><FileText size={15} /> {draft.id ? "Private note" : "New note"}{statusLabel && <span className={saveState === "error" || saveState === "conflict" ? "text-amber-200" : saveState === "saved" ? "text-emerald-300" : "text-slate-400"}>· {statusLabel}</span>}</div><div className="flex flex-wrap gap-2"><button type="button" onClick={() => void saveNow()} disabled={saveState === "saving"} className="rounded-lg border border-indigo-400/40 px-3 py-2 text-xs font-semibold text-indigo-200 hover:bg-indigo-500/10 disabled:opacity-50">Save</button>{draft.id && <button type="button" onClick={() => void exportNote()} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300 hover:border-indigo-400 hover:text-white"><Download size={14} className="mr-1 inline" />Export</button>}{draft.id && <button type="button" onClick={() => void removeNote()} className="rounded-lg border border-red-400/20 px-3 py-2 text-xs text-red-200 hover:bg-red-400/10"><Trash2 size={14} className="mr-1 inline" />Delete</button>}</div></div><input value={draft.title} onChange={event => updateDraft({ title: event.target.value })} placeholder="Note title" className="mt-5 w-full bg-transparent text-2xl font-bold text-slate-100 outline-none placeholder:text-slate-700" maxLength={240} /><div className="mt-4 grid gap-3 sm:grid-cols-2"><input value={draft.course_id} onChange={event => updateDraft({ course_id: event.target.value })} placeholder="Course ID (optional)" className="rounded-lg border border-line bg-ink/40 px-3 py-2 text-xs text-slate-300 outline-none focus:border-indigo-400" /><input value={draft.lesson_id} onChange={event => updateDraft({ lesson_id: event.target.value })} placeholder="Lesson ID (optional)" className="rounded-lg border border-line bg-ink/40 px-3 py-2 text-xs text-slate-300 outline-none focus:border-indigo-400" /></div><div className="mt-3 grid gap-3 sm:grid-cols-[1fr_1fr_auto_auto]"><select value={draft.folder_id} onChange={event => updateDraft({ folder_id: event.target.value })} className="rounded-lg border border-line bg-ink/40 px-3 py-2 text-xs text-slate-300 outline-none"><option value="">No folder</option>{folders.map(folder => <option key={folder.id} value={folder.id}>{folder.name}</option>)}</select><input value={draft.tags.join(", ")} onChange={event => updateDraft({ tags: event.target.value.split(",").map(value => value.trim()).filter(Boolean) })} placeholder="Tags, comma separated" className="rounded-lg border border-line bg-ink/40 px-3 py-2 text-xs text-slate-300 outline-none focus:border-indigo-400" /><button type="button" aria-pressed={draft.is_favorite} onClick={() => updateDraft({ is_favorite: !draft.is_favorite })} className={`rounded-lg border px-3 py-2 text-xs ${draft.is_favorite ? "border-amber-400/50 bg-amber-400/10 text-amber-200" : "border-line text-slate-400"}`}>★ Favorite</button><button type="button" aria-pressed={draft.is_pinned} onClick={() => updateDraft({ is_pinned: !draft.is_pinned })} className={`rounded-lg border px-3 py-2 text-xs ${draft.is_pinned ? "border-indigo-400/50 bg-indigo-400/10 text-indigo-200" : "border-line text-slate-400"}`}>⌖ Pin</button></div>{(context.courseSlug && context.lessonSlug) && <Link href={`/learn/${context.courseSlug}/${context.lessonSlug}`} className="mt-3 inline-block text-xs text-indigo-300 hover:text-white">← Return to lesson</Link>}{saveError && <div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-100">{saveError} {saveState === "error" && <button type="button" onClick={() => void saveNow()} className="ml-2 font-semibold underline">Retry</button>}</div>}<div className="mt-5 overflow-hidden rounded-xl border border-line bg-ink/35"><div className="flex items-center justify-between border-b border-line px-3 py-2"><Toolbar onInsert={insertMarkdown} /><button type="button" onClick={() => setPreview(value => !value)} className="rounded-lg px-2 py-1 text-xs text-indigo-300 hover:bg-indigo-500/10">{preview ? "Edit" : "Preview"}</button></div>{preview ? <div className="min-h-[360px] p-4"><MarkdownPreview value={draft.content} /></div> : <textarea ref={textareaRef} value={draft.content} onChange={event => updateDraft({ content: event.target.value })} placeholder="Write your learning note in Markdown…" className="min-h-[360px] w-full resize-y bg-transparent p-4 font-mono text-sm leading-7 text-slate-200 outline-none placeholder:text-slate-700" spellCheck />}</div></> : <div className="grid min-h-[520px] place-items-center text-center"><div><FileText className="mx-auto text-slate-700" size={36} /><h2 className="mt-4 text-lg font-semibold text-slate-200">Choose a note to edit</h2><p className="mt-2 max-w-sm text-sm text-slate-500">Your notes stay private to your account and autosave after the server confirms each change.</p><button type="button" onClick={newNote} className="mt-5 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500">Create your first note</button></div></div>}</section>
    </div>
  </div>;
}

export function LessonNotes({ courseId, lessonId, courseSlug, lessonSlug }: { courseId: string; lessonId: string; courseSlug: string; lessonSlug: string }) {
  const [notes, setNotes] = useState<PersonalNote[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "anonymous">("loading");
  useEffect(() => {
    let active = true;
    notesApi.list(`?lesson_id=${encodeURIComponent(lessonId)}&page_size=20&sort=updated_at&order=desc`).then(result => { if (active) { setNotes(result.items); setState("ready"); } }).catch(() => { if (active) setState("anonymous"); });
    return () => { active = false; };
  }, [lessonId]);
  if (state === "anonymous") return <aside className="mb-8 rounded-2xl border border-indigo-400/20 bg-indigo-500/[0.06] p-4"><p className="text-sm font-semibold text-indigo-100">My notes</p><p className="mt-1 text-xs text-slate-400">Sign in to keep private notes linked to this lesson.</p></aside>;
  return <aside className="mb-8 rounded-2xl border border-indigo-400/20 bg-indigo-500/[0.06] p-4" aria-label="Lesson notes"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-semibold text-indigo-100">My notes</p><p className="mt-1 text-xs text-slate-400">Keep a private reference beside the lesson.</p></div><Link href={`/dashboard/notebook?new=1&course_id=${encodeURIComponent(courseId)}&lesson_id=${encodeURIComponent(lessonId)}&course_slug=${encodeURIComponent(courseSlug)}&lesson_slug=${encodeURIComponent(lessonSlug)}`} className="rounded-lg bg-indigo-500/20 px-3 py-2 text-xs font-semibold text-indigo-200 hover:bg-indigo-500/30">+ Add note</Link></div>{state === "loading" ? <p className="mt-3 text-xs text-slate-500">Loading notes…</p> : notes.length ? <div className="mt-3 flex flex-wrap gap-2">{notes.map(note => <Link key={note.id} href={`/dashboard/notebook?note=${note.id}&course_slug=${encodeURIComponent(courseSlug)}&lesson_slug=${encodeURIComponent(lessonSlug)}`} className="rounded-lg border border-line bg-ink/30 px-3 py-2 text-xs text-slate-300 hover:border-indigo-400 hover:text-white">{note.title || "Untitled note"}</Link>)}</div> : <p className="mt-3 text-xs text-slate-500">No notes for this lesson yet.</p>}</aside>;
}
