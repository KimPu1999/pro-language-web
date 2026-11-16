"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, Search, Tags, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ApiError, api } from "@/lib/api";
import type { Enrollment } from "@/lib/types";
import { Card, Skeleton } from "@/components/ui";

type ViewMode = "grid" | "list";
type SortMode = "recent" | "progress" | "title";

const clamp = (value: number) => Math.min(100, Math.max(0, Number.isFinite(value) ? value : 0));

export function StudentCoursesPage() {
  const [items, setItems] = useState<Enrollment[] | null>(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [category, setCategory] = useState("all");
  const [level, setLevel] = useState("all");
  const [sort, setSort] = useState<SortMode>("recent");
  const [view, setView] = useState<ViewMode>("grid");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const pageSize = 10;

  const load = () => {
    setError("");
    setItems(null);
    api.enrollments().then(setItems).catch(reason => {
      if (reason instanceof ApiError && reason.status === 401) {
        window.location.href = `/login?next=${encodeURIComponent("/dashboard/courses")}`;
        return;
      }
      setError(reason instanceof Error ? reason.message : "Unable to load your courses.");
    });
  };

  useEffect(load, []);
  useEffect(() => setPage(1), [query, status, category, level, sort]);

  const categories = useMemo(() => Array.from(new Set((items ?? []).map(item => item.course.category.name).filter(Boolean))).sort(), [items]);
  const levels = useMemo(() => Array.from(new Set((items ?? []).map(item => item.course.level).filter(Boolean))).sort(), [items]);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return [...(items ?? [])]
      .filter(item => !normalized || `${item.course.title} ${item.course.description}`.toLowerCase().includes(normalized))
      .filter(item => status === "all" || (status === "completed" ? item.progress_percent >= 100 : status === "in_progress" ? item.progress_percent > 0 && item.progress_percent < 100 : item.progress_percent === 0))
      .filter(item => category === "all" || item.course.category.name === category)
      .filter(item => level === "all" || item.course.level === level)
      .sort((a, b) => sort === "title" ? a.course.title.localeCompare(b.course.title) : sort === "progress" ? b.progress_percent - a.progress_percent : 0);
  }, [items, query, status, category, level, sort]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const visible = filtered.slice((page - 1) * pageSize, page * pageSize);

  return <div className="mx-auto max-w-[1280px]">
    <div className="flex flex-wrap items-end justify-between gap-5">
      <div><p className="text-xs font-semibold uppercase tracking-[.18em] text-indigo-300">Your library</p><h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">My courses</h1><p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">Manage your enrolled courses and continue from your verified progress.</p></div>
      <Link href="/courses" className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500">Browse catalog <ArrowRight size={16} /></Link>
    </div>
    <div className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
      {[{ label: "Enrolled", value: items?.length ?? 0 }, { label: "In progress", value: items?.filter(item => item.progress_percent > 0 && item.progress_percent < 100).length ?? 0 }, { label: "Completed", value: items?.filter(item => item.progress_percent >= 100).length ?? 0 }, { label: "Not started", value: items?.filter(item => item.progress_percent === 0).length ?? 0 }].map(stat => <Card className="p-4" key={stat.label}><p className="text-xs font-medium uppercase tracking-[.12em] text-slate-500">{stat.label}</p><p className="mt-2 text-2xl font-bold text-slate-100">{items ? stat.value : "—"}</p></Card>)}
    </div>
    <div className="mt-7 rounded-2xl border border-line/70 bg-surface/70 p-3 sm:p-4">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center">
        <label className="relative min-w-0 flex-1"><Search className="absolute left-3 top-3 text-slate-500" size={17} /><input aria-label="Search enrolled courses" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search enrolled courses…" className="w-full rounded-xl border border-line bg-ink/60 py-2.5 pl-10 pr-10 text-sm outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/10" />{query && <button type="button" aria-label="Clear course search" onClick={() => setQuery("")} className="absolute right-2 top-2 rounded-lg p-1 text-slate-500 hover:text-white"><X size={15} /></button>}</label>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:flex"><label className="flex items-center gap-2 rounded-xl border border-line bg-ink/50 px-3 text-sm text-slate-400"><Tags size={16} /><select aria-label="Filter course status" value={status} onChange={event => setStatus(event.target.value)} className="min-w-0 bg-transparent py-2.5 text-slate-200 outline-none"><option value="all">All status</option><option value="in_progress">In progress</option><option value="completed">Completed</option><option value="not_started">Not started</option></select></label><select aria-label="Filter course category" value={category} onChange={event => setCategory(event.target.value)} className="rounded-xl border border-line bg-ink/50 px-3 py-2.5 text-sm text-slate-300 outline-none"><option value="all">All categories</option>{categories.map(value => <option key={value} value={value}>{value}</option>)}</select><select aria-label="Filter course level" value={level} onChange={event => setLevel(event.target.value)} className="rounded-xl border border-line bg-ink/50 px-3 py-2.5 text-sm text-slate-300 outline-none"><option value="all">All levels</option>{levels.map(value => <option key={value} value={value}>{value}</option>)}</select><select aria-label="Sort courses" value={sort} onChange={event => setSort(event.target.value as SortMode)} className="rounded-xl border border-line bg-ink/50 px-3 py-2.5 text-sm text-slate-300 outline-none"><option value="recent">Recently added</option><option value="progress">Progress</option><option value="title">Title</option></select></div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-line/50 pt-3"><p className="text-xs text-slate-500">{items ? `${filtered.length} course${filtered.length === 1 ? "" : "s"} in this view` : "Loading your library…"}</p><div className="flex rounded-lg border border-line bg-ink/50 p-1"><button type="button" aria-label="Grid view" aria-pressed={view === "grid"} onClick={() => setView("grid")} className={`rounded-md px-3 py-1.5 text-xs ${view === "grid" ? "bg-indigo-500/20 text-indigo-200" : "text-slate-500"}`}>Grid</button><button type="button" aria-label="List view" aria-pressed={view === "list"} onClick={() => setView("list")} className={`rounded-md px-3 py-1.5 text-xs ${view === "list" ? "bg-indigo-500/20 text-indigo-200" : "text-slate-500"}`}>List</button></div></div>
    </div>
    {error ? <div className="mt-7" role="alert"><Card className="border-red-400/20 bg-red-500/[.06] p-6"><p className="text-sm text-red-200">{error}</p><button type="button" onClick={load} className="mt-4 rounded-lg bg-red-400/15 px-3 py-2 text-sm font-semibold text-red-100">Retry</button></Card></div> : !items ? <div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{[1, 2, 3].map(index => <Skeleton className="h-56" key={index} />)}</div> : items.length === 0 ? <EmptyState title="Your learning library is ready" description="You have no enrolled courses yet. Explore the catalog and start building verified learning progress." /> : filtered.length === 0 ? <EmptyState title="No courses match these filters" description="Try clearing your search or selecting a different status, category, or level." action={<button type="button" onClick={() => { setQuery(""); setStatus("all"); setCategory("all"); setLevel("all"); }} className="rounded-xl border border-line px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-elevated">Clear filters</button>} /> : <><div className={view === "grid" ? "mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-3" : "mt-7 space-y-3"}>{visible.map(item => <CourseCard item={item} list={view === "list"} key={item.id} />)}</div>{pageCount > 1 && <div className="mt-6 flex items-center justify-between"><p className="text-xs text-slate-500">Page {page} of {pageCount}</p><div className="flex gap-2"><button type="button" disabled={page === 1} onClick={() => setPage(value => value - 1)} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-300 disabled:cursor-not-allowed disabled:opacity-40">Previous</button><button type="button" disabled={page === pageCount} onClick={() => setPage(value => value + 1)} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-300 disabled:cursor-not-allowed disabled:opacity-40">Next</button></div></div>}</>}
  </div>;
}

function CourseCard({ item, list }: { item: Enrollment; list: boolean }) {
  const progress = clamp(item.progress_percent);
  const targetSlug = item.next_lesson_slug ?? item.last_lesson_slug;
  const target = targetSlug ? `/courses/${item.course.slug}/learn/${targetSlug}` : `/courses/${item.course.slug}`;
  return <Card className={list ? "p-4 sm:flex sm:items-center sm:gap-5" : "p-5 transition hover:-translate-y-0.5 hover:border-indigo-400/30"}><div className="flex min-w-0 flex-1 items-start gap-4"><div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-indigo-500/15 text-indigo-300"><BookOpen size={20} /></div><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-medium uppercase tracking-[.12em] text-slate-500">{item.course.category.name} · {item.course.level}</p><h2 className="mt-1 line-clamp-2 font-semibold text-slate-100">{item.course.title}</h2></div><span className="text-xs font-semibold text-slate-400">{Math.round(progress)}%</span></div><p className="mt-2 text-xs text-slate-500">{item.completed_lessons} of {item.total_lessons} lessons complete</p><div className="mt-4 h-1.5 rounded-full bg-elevated"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-400" style={{ width: `${progress}%` }} /></div></div></div><div className="mt-5 flex items-center justify-between gap-3 sm:mt-4"><span className="text-xs text-slate-500">{progress >= 100 ? "Completed" : progress > 0 ? "In progress" : "Not started"}</span><div className="flex gap-3"><Link href={`/courses/${item.course.slug}`} className="text-sm font-medium text-slate-400 hover:text-white">Curriculum</Link><Link href={target} className="inline-flex items-center gap-1 text-sm font-medium text-indigo-300 hover:text-white">{progress >= 100 ? "Review" : "Resume"} <ArrowRight size={14} /></Link></div></div></Card>;
}

function EmptyState({ title, description, action }: { title: string; description: string; action?: React.ReactNode }) {
  return <Card className="mt-7 overflow-hidden border-indigo-400/10 bg-gradient-to-br from-surface to-[#101a30] p-8 sm:p-12"><div className="mx-auto max-w-lg text-center"><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-indigo-500/15 text-indigo-300"><BookOpen size={28} /></div><h2 className="mt-5 text-xl font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>{action ?? <Link href="/courses" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white">Browse courses <ArrowRight size={15} /></Link>}</div></Card>;
}
