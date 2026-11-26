"use client";

import Link from "next/link";
import { BookOpen, Check, ChevronRight, DatabaseBackup, Eye, ListChecks, RefreshCw, Search, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { curriculumQualityApi } from "@/lib/api";
import type { CurriculumQualityDetail, CurriculumQualityItem } from "@/lib/types";
import { csrf } from "@/components/auth-form";
import { Badge, Button, Card, EmptyState, Skeleton } from "@/components/ui";

const levels = ["beginner", "intermediate", "advanced", "professional"];
const auditStatuses = ["published_with_gaps", "draft_with_gaps", "review_pending", "ready_for_review", "published_ready_for_review"];
type AuditSummary = { courses: number; published_courses: number; courses_with_gaps: number; review_pending: number; modules: number; lessons: number; published_lessons: number; syntax_references: number };

function label(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusClass(value: string) {
  if (value.includes("gap")) return "bg-amber-400/10 text-amber-200";
  if (value === "review_pending") return "bg-sky-400/10 text-sky-200";
  return "bg-emerald-400/10 text-emerald-300";
}

function GapList({ title, items }: { title: string; items: string[] }) {
  return <div>
    <div className="flex items-center justify-between gap-3">
      <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      <span className="text-xs text-slate-500">{items.length}</span>
    </div>
    {items.length ? <ul className="mt-2 space-y-1.5 text-sm text-slate-400">{items.slice(0, 8).map((item) => <li key={item} className="flex gap-2"><span className="text-amber-300">•</span><span>{item}</span></li>)}{items.length > 8 && <li className="text-xs text-slate-500">+ {items.length - 8} more records</li>}</ul> : <p className="mt-2 text-sm text-emerald-300">No records in this category.</p>}
  </div>;
}

export default function CurriculumQualityPage() {
  const [items, setItems] = useState<CurriculumQualityItem[]>([]);
  const [summary, setSummary] = useState<AuditSummary>({ courses: 0, published_courses: 0, courses_with_gaps: 0, review_pending: 0, modules: 0, lessons: 0, published_lessons: 0, syntax_references: 0 });
  const [selected, setSelected] = useState<CurriculumQualityDetail | null>(null);
  const [technology, setTechnology] = useState("");
  const [level, setLevel] = useState("");
  const [completeness, setCompleteness] = useState("");
  const [reviewStatus, setReviewStatus] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (technology) params.set("technology", technology);
    if (level) params.set("level", level);
    if (completeness) params.set("completeness", completeness);
    if (reviewStatus) params.set("review_status", reviewStatus);
    if (search.trim()) params.set("search", search.trim());
    return params.toString() ? `?${params.toString()}` : "";
  }, [technology, level, completeness, reviewStatus, search]);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await curriculumQualityApi.list(query);
      setItems(result.items);
      setSummary(result.summary);
    }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to load the curriculum audit."); }
    finally { setLoading(false); }
  }, [query]);

  useEffect(() => { void load(); }, [load]);

  const technologies = useMemo(() => Array.from(new Set(items.map((item) => item.technology_slug).filter((value): value is string => Boolean(value)))).sort(), [items]);

  async function openDetail(id: string) {
    setDetailLoading(true);
    setError("");
    try { setSelected(await curriculumQualityApi.detail(id)); }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to load the course audit."); }
    finally { setDetailLoading(false); }
  }

  async function submitReview(id: string) {
    setMessage("");
    setError("");
    try {
      const result = await curriculumQualityApi.submitReview(id, csrf());
      setMessage(result.created ? "Course submitted to Content Review." : "An active Content Review item already exists for this course.");
      await load();
      await openDetail(id);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to submit the course for review."); }
  }

  const metrics = [
    { label: "Courses in audit", value: summary.courses, detail: `${summary.published_courses} published`, icon: DatabaseBackup, tone: "text-indigo-300" },
    { label: "Curriculum gaps", value: summary.courses_with_gaps, detail: "needs review or content", icon: ListChecks, tone: "text-amber-300" },
    { label: "Learning structure", value: summary.modules, detail: `${summary.lessons} lessons · ${summary.published_lessons} published`, icon: BookOpen, tone: "text-cyan-300" },
    { label: "Review queue", value: summary.review_pending, detail: `${summary.syntax_references} syntax references`, icon: RefreshCw, tone: "text-emerald-300" },
  ];

  return <section className="mx-auto max-w-[1500px] space-y-5">
    <div className="flex flex-wrap items-end justify-between gap-5">
      <div>
        <div className="flex items-center gap-2 text-sm font-semibold text-indigo-300"><span className="grid h-7 w-7 place-items-center rounded-lg bg-indigo-400/10"><DatabaseBackup size={15}/></span>Evidence based curriculum audit</div>
        <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-[40px]">Curriculum Quality Center</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">Inspect actual course, module, lesson, quiz, exercise, syntax, project, and review records. Every count below comes from live database records.</p>
      </div>
      <Button className="inline-flex items-center gap-2 border border-line bg-surface text-slate-200 hover:bg-elevated" onClick={() => void load()}><RefreshCw size={16}/>Refresh audit</Button>
    </div>

    {error && <Card className="border-red-400/20 bg-red-500/5 p-4 text-sm text-red-300">{error}</Card>}
    {message && <Card className="border-emerald-400/20 bg-emerald-500/5 p-4 text-sm text-emerald-300">{message}</Card>}

    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map(({ label: metricLabel, value, detail, icon: Icon, tone }) => <Card key={metricLabel} className="relative overflow-hidden p-4 sm:p-5"><div className="absolute right-4 top-4 rounded-xl bg-white/[0.03] p-2"><Icon size={17} className={tone}/></div><p className="text-xs font-medium text-slate-500">{metricLabel}</p><p className="mt-2 text-2xl font-bold tracking-tight text-slate-100">{value.toLocaleString()}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></Card>)}
    </div>

    <Card className="p-4 sm:p-5">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <label className="flex items-center gap-2 rounded-xl border border-line bg-ink/40 px-3 text-sm text-slate-500 focus-within:border-indigo-400/60 md:col-span-2 xl:col-span-1"><Search size={16}/><input aria-label="Search courses" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search courses…" className="min-w-0 flex-1 bg-transparent py-3 text-slate-200 outline-none placeholder:text-slate-600"/></label>
        <select aria-label="Filter technology" value={technology} onChange={(event) => setTechnology(event.target.value)} className="rounded-xl border border-line bg-ink/40 px-3 py-3 text-sm text-slate-300"><option value="">All technologies</option>{technologies.map((value) => <option key={value} value={value}>{value}</option>)}</select>
        <select aria-label="Filter level" value={level} onChange={(event) => setLevel(event.target.value)} className="rounded-xl border border-line bg-ink/40 px-3 py-3 text-sm text-slate-300"><option value="">All levels</option>{levels.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select>
        <select aria-label="Filter curriculum status" value={completeness} onChange={(event) => setCompleteness(event.target.value)} className="rounded-xl border border-line bg-ink/40 px-3 py-3 text-sm text-slate-300"><option value="">All audit states</option>{auditStatuses.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select>
        <select aria-label="Filter review status" value={reviewStatus} onChange={(event) => setReviewStatus(event.target.value)} className="rounded-xl border border-line bg-ink/40 px-3 py-3 text-sm text-slate-300"><option value="">All review states</option><option value="none">No review item</option><option value="submitted">Submitted</option><option value="in_review">In review</option><option value="approved">Approved</option><option value="changes_requested">Changes requested</option><option value="rejected">Rejected</option></select>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-line/70 pt-3 text-xs text-slate-500"><span>Filters query live database records.</span><span>{items.length.toLocaleString()} course records shown</span></div>
    </Card>

    {loading ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><Skeleton className="h-56"/><Skeleton className="h-56"/><Skeleton className="h-56"/></div> : items.length ? <div className="grid gap-4 xl:grid-cols-2">{items.map((item) => <Card key={item.id} className="overflow-hidden">
      <div className="border-b border-line/80 bg-surface/70 p-5"><div className="flex flex-wrap items-start justify-between gap-3"><div className="min-w-0"><p className="truncate font-mono text-[11px] text-slate-500">{item.slug}</p><h2 className="mt-1 text-lg font-semibold text-slate-100">{item.title}</h2><p className="mt-1 text-sm text-slate-400">{item.technology ?? "Technology not linked"} · {label(item.course_level)}</p></div><Badge className={statusClass(item.audit_status)}>{label(item.audit_status)}</Badge></div></div>
      <div className="grid grid-cols-3 divide-x divide-line/70 border-b border-line/70"><div className="p-4"><p className="text-xs text-slate-500">Modules</p><p className="mt-1 text-xl font-semibold">{item.module_count}</p></div><div className="p-4"><p className="text-xs text-slate-500">Lessons</p><p className="mt-1 text-xl font-semibold">{item.lesson_count}</p></div><div className="p-4"><p className="text-xs text-slate-500">Evidence gaps</p><p className="mt-1 text-xl font-semibold text-amber-200">{item.gaps.length}</p></div></div>
      <div className="p-5"><div className="flex flex-wrap gap-2 text-xs">{Object.entries(item.level_coverage).map(([key, present]) => <span key={key} className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 ${present ? "bg-emerald-400/10 text-emerald-300" : "bg-slate-800 text-slate-500"}`}>{present ? <Check size={12}/> : <X size={12}/>} {label(key)}</span>)}</div><p className="mt-3 text-xs text-slate-500">{item.review ? `Review: ${label(item.review.status)} · v${item.review.version}` : "No Content Review item exists for this course."}</p><div className="mt-5 flex flex-wrap items-center gap-2"><button onClick={() => void openDetail(item.id)} className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500"><Eye size={14}/>Audit</button><Link href={`/admin/courses/${item.id}/builder`} className="rounded-lg border border-line px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-elevated">Edit curriculum</Link><Link href="/platform/content-review" className="rounded-lg border border-line px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-elevated">Review content</Link><Link href={`/courses/${item.slug}`} target="_blank" className="rounded-lg border border-line px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-elevated">Preview</Link><button onClick={() => void submitReview(item.id)} className="ml-auto inline-flex items-center gap-1 text-xs font-semibold text-indigo-300 hover:text-indigo-200">Submit review <ChevronRight size={14}/></button></div></div>
    </Card>)}</div> : <Card className="p-8"><EmptyState title="No courses match these filters" description="Clear a filter or refresh the audit after course records are available."/></Card>}

    {selected && <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-0 sm:items-center sm:p-6" role="dialog" aria-modal="true" aria-label="Course curriculum audit"><div className="max-h-[92vh] w-full max-w-6xl overflow-y-auto rounded-t-2xl border border-line bg-ink shadow-2xl sm:rounded-2xl"><div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-line bg-ink/95 p-5 backdrop-blur"><div><p className="font-mono text-[11px] text-slate-500">{selected.slug}</p><h2 className="mt-1 text-2xl font-bold">{selected.title}</h2><p className="mt-1 text-sm text-slate-400">{selected.data_source}</p></div><button aria-label="Close course audit" onClick={() => setSelected(null)} className="rounded-lg p-2 text-slate-400 hover:bg-surface hover:text-white"><X size={20}/></button></div>{detailLoading ? <div className="grid gap-4 p-5 md:grid-cols-2"><Skeleton className="h-44"/><Skeleton className="h-44"/></div> : <div className="space-y-5 p-5"><div className="flex flex-wrap items-center gap-2"><Badge className={statusClass(selected.audit_status)}>{label(selected.audit_status)}</Badge><span className="text-sm text-slate-400">{selected.module_count} modules · {selected.lesson_count} lessons · {selected.published_lesson_count} published lessons</span><span className="text-sm text-amber-200">{selected.gaps.length} evidence gap categories</span><Button className="ml-auto" onClick={() => void submitReview(selected.id)}>Submit to Content Review</Button></div><div className="grid gap-5 lg:grid-cols-2"><Card className="space-y-5 p-5"><GapList title="Missing course metadata" items={selected.missing_course_metadata}/><GapList title="Missing expected topics" items={selected.missing_topics}/><GapList title="Empty or incorrectly ordered modules" items={selected.missing_modules}/><GapList title="Empty or incorrectly ordered lessons" items={selected.missing_lessons}/><GapList title="Duplicate lesson slugs" items={selected.duplicate_lesson_slugs}/></Card><Card className="space-y-5 p-5"><GapList title="Lessons with incomplete required sections" items={selected.missing_lesson_sections.map((entry) => `${entry.title}: ${entry.missing.join(", ")}`)}/><GapList title="Missing code examples" items={selected.missing_code_examples}/><GapList title="Missing quizzes" items={selected.missing_quizzes}/><GapList title="Missing exercises" items={selected.missing_exercises}/><GapList title="Published syntax references with fewer than 5 examples" items={selected.syntax_gaps.map((entry) => `${entry.title}: ${entry.example_count}/5 examples`)}/></Card></div><Card className="overflow-hidden"><div className="border-b border-line p-5"><h3 className="font-semibold">Lesson level evidence</h3><p className="mt-1 text-xs text-slate-500">Section signals are based on stored English lesson content and related records.</p></div><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="border-b border-line bg-surface/60 text-xs uppercase tracking-[0.12em] text-slate-500"><tr><th className="px-5 py-3">Lesson</th><th className="px-5 py-3">Order</th><th className="px-5 py-3">Code</th><th className="px-5 py-3">Quiz</th><th className="px-5 py-3">Exercises</th><th className="px-5 py-3">Missing sections</th></tr></thead><tbody className="divide-y divide-line/70">{selected.lessons.map((lesson) => <tr key={lesson.id}><td className="px-5 py-3"><p className="font-medium text-slate-200">{lesson.title}</p><p className="text-xs text-slate-500">{lesson.status} · {lesson.published ? "published" : "draft"}</p></td><td className="px-5 py-3 text-slate-400">{lesson.order_index}</td><td className="px-5 py-3 text-slate-400">{lesson.code_examples}</td><td className="px-5 py-3 text-slate-400">{lesson.quiz_questions}</td><td className="px-5 py-3 text-slate-400">{lesson.exercises}</td><td className="max-w-xs px-5 py-3 text-xs text-amber-200">{lesson.missing_sections.length ? lesson.missing_sections.join(", ") : "Complete by audit rules"}</td></tr>)}</tbody></table></div></Card><div className="flex flex-wrap gap-3"><Link href={`/admin/courses/${selected.id}/builder`} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white">Edit curriculum <ChevronRight size={16}/></Link><Link href="/platform/content-review" className="inline-flex items-center gap-2 rounded-xl border border-line px-4 py-2.5 text-sm font-semibold text-slate-300">Review queue <ChevronRight size={16}/></Link></div></div>}</div></div>}
  </section>;
}
