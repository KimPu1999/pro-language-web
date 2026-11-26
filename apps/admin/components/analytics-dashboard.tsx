"use client";

import { Activity, BarChart3, BookOpen, CheckCircle2, Clock3, FolderKanban, GraduationCap, RefreshCw, Send, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { AdminDataTable, AdminStatCard, Breadcrumbs, Button, EmptyState, ErrorState, PageHeader, Panel, Spinner, StatusBadge } from "@/components/ui";

type AnalyticsData = { overview: any; courses: any; challenges: any; projects: any };

function isoDate(value: Date) { return value.toISOString().slice(0, 10); }
function apiUrl(path: string, start: string, end: string) { const query = new URLSearchParams({ start_date: start, end_date: end }); return `${path}?${query}`; }
async function read<T>(path: string): Promise<T> {
  const response = await fetch(path, { credentials: "include", headers: { Accept: "application/json" }, cache: "no-store" });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof body.detail === "string" ? body.detail : `Analytics request failed (${response.status}).`);
  return body;
}

function TrendChart({ trends }: { trends: any[] }) {
  const sample = trends.length > 14 ? trends.filter((_: any, index: number) => index % Math.ceil(trends.length / 14) === 0) : trends;
  const max = Math.max(1, ...sample.map(item => Math.max(Number(item.enrollments || 0), Number(item.lesson_completions || 0))));
  if (!sample.length) return <EmptyState title="No activity in this period" description="Enrollment and lesson activity will appear here when records exist." />;
  return <div aria-label="Enrollment and lesson completion trend" className="flex h-56 items-end gap-2 overflow-x-auto px-2 pb-7 pt-5">{sample.map(item => <div key={item.date} className="flex h-full min-w-7 flex-1 flex-col items-center justify-end gap-1"><div className="flex h-full w-full items-end justify-center gap-1"><span title={`${item.enrollments} enrollments`} className="w-2 rounded-t bg-primary/80" style={{ height: `${Math.max(3, Number(item.enrollments || 0) / max * 100)}%` }} /><span title={`${item.lesson_completions} lesson completions`} className="w-2 rounded-t bg-accent/70" style={{ height: `${Math.max(3, Number(item.lesson_completions || 0) / max * 100)}%` }} /></div><span className="text-[10px] text-muted">{String(item.date).slice(5)}</span></div>)}</div>;
}

export default function AnalyticsDashboard() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [applied, setApplied] = useState({ start: "", end: "" });
  const [data, setData] = useState<AnalyticsData>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true); setError("");
    try {
      const [overview, courses, challenges, projects] = await Promise.all([
        read<any>(apiUrl("/api/v1/platform/analytics/overview", applied.start, applied.end)),
        read<any>(apiUrl("/api/v1/platform/analytics/courses", applied.start, applied.end)),
        read<any>(apiUrl("/api/v1/platform/analytics/challenges", applied.start, applied.end)),
        read<any>(apiUrl("/api/v1/platform/analytics/projects", applied.start, applied.end)),
      ]);
      setData({ overview, courses, challenges, projects });
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load analytics."); }
    finally { setLoading(false); }
  }
  useEffect(() => { const endDate = new Date(); const startDate = new Date(endDate.getTime() - 29 * 86400000); const next = { start: isoDate(startDate), end: isoDate(endDate) }; setStart(next.start); setEnd(next.end); setApplied(next); }, []);
  useEffect(() => { if (!applied.start || !applied.end) return; void load(); }, [applied.start, applied.end]);

  const kpis = data?.overview?.kpis || {};
  const courseRows = data?.courses?.items || [];
  const difficultyRows = data?.challenges?.difficulty_performance || [];
  const definitions = data?.overview?.definitions || {};
  const completion = data?.overview?.completion_rate ?? 0;
  const cards = useMemo(() => [
    ["Total students", kpis.total_students ?? 0, <Users size={18} />, "All student accounts"],
    ["New registrations", kpis.new_registrations ?? 0, <GraduationCap size={18} />, "Selected period"],
    ["Active learners", kpis.active_students ?? 0, <Activity size={18} />, "Distinct students with activity"],
    ["Total enrollments", kpis.total_enrollments ?? 0, <BookOpen size={18} />, "Selected period"],
    ["Completed courses", kpis.completed_courses ?? 0, <CheckCircle2 size={18} />, `${completion}% completion rate`],
    ["Challenge submissions", kpis.challenge_submissions ?? 0, <Send size={18} />, "Selected period"],
    ["Project submissions", data?.projects?.submitted ?? 0, <FolderKanban size={18} />, "Selected period"],
  ], [data, kpis, completion]);

  return <section>
    <Breadcrumbs items={[{ label: "Admin", href: "/dashboard" }, { label: "Analytics" }]} />
    <PageHeader eyebrow="Platform intelligence" title="Analytics" description="Database-backed learning, course, challenge, and project performance for the selected UTC period." actions={<Button variant="secondary" onClick={() => void load()} disabled={loading}><RefreshCw size={16} /> Refresh</Button>} />
    <Panel className="mt-6 p-4"><form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={event => { event.preventDefault(); if (start <= end) setApplied({ start, end }); else setError("Start date must be on or before end date."); }}><label className="text-xs font-medium text-muted">From<input type="date" value={start} onChange={event => setStart(event.target.value)} className="mt-1 block h-10 rounded-xl border border-line bg-ink px-3 text-sm text-foreground" /></label><label className="text-xs font-medium text-muted">To<input type="date" value={end} onChange={event => setEnd(event.target.value)} className="mt-1 block h-10 rounded-xl border border-line bg-ink px-3 text-sm text-foreground" /></label><Button type="submit">Apply dates</Button><span className="text-xs text-muted">UTC · {data?.overview?.range?.start || applied.start} to {data?.overview?.range?.end || applied.end}</span></form></Panel>
    {error && <div className="mt-6"><ErrorState message={error} /></div>}
    {loading && !data ? <Panel className="mt-6 p-8"><div className="flex items-center gap-3 text-sm text-muted"><Spinner /> Loading live analytics…</div></Panel> : data && <>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{cards.map(([label, value, icon, detail]) => <AdminStatCard key={String(label)} label={String(label)} value={value as number} icon={icon} detail={String(detail)} />)}</div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,1fr)]"><Panel className="p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold">Learning activity</h2><p className="mt-1 text-xs text-muted">Enrollments and completed lessons by day.</p></div><div className="flex gap-3 text-xs text-muted"><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-primary" />Enrollments</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-accent" />Lesson completions</span></div></div><TrendChart trends={data.overview.trends || []} /></Panel><Panel className="p-5"><div className="flex items-center gap-2"><Clock3 size={17} className="text-primary" /><h2 className="font-semibold">Project review queue</h2></div><div className="mt-5 grid grid-cols-2 gap-3"><div className="rounded-xl bg-surface-hover p-3"><p className="text-xs text-muted">Pending review</p><p className="mt-2 text-2xl font-semibold">{data.projects.pending_reviews}</p></div><div className="rounded-xl bg-surface-hover p-3"><p className="text-xs text-muted">Approved</p><p className="mt-2 text-2xl font-semibold">{data.projects.approved}</p></div><div className="rounded-xl bg-surface-hover p-3"><p className="text-xs text-muted">Revision requests</p><p className="mt-2 text-2xl font-semibold">{data.projects.revision_requests}</p></div><div className="rounded-xl bg-surface-hover p-3"><p className="text-xs text-muted">Published projects</p><p className="mt-2 text-2xl font-semibold">{data.projects.published_projects}</p></div></div></Panel></div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(320px,1fr)]"><Panel className="overflow-hidden"><div className="flex items-center gap-2 border-b border-line p-5"><BarChart3 size={17} className="text-primary" /><div><h2 className="font-semibold">Course performance</h2><p className="mt-1 text-xs text-muted">Popular published courses, progress activity, and completion rates.</p></div></div>{courseRows.length ? <AdminDataTable className="rounded-none border-0"><thead className="border-b border-line text-xs uppercase tracking-wider text-muted"><tr><th className="px-5 py-3">Course</th><th className="px-5 py-3">Enrollments</th><th className="px-5 py-3">Lesson activity</th><th className="px-5 py-3">Completion</th></tr></thead><tbody className="divide-y divide-line">{courseRows.slice(0, 8).map((course: any) => <tr key={course.id}><td className="px-5 py-4 font-medium">{course.title}</td><td className="px-5 py-4">{course.enrollments}</td><td className="px-5 py-4">{course.lesson_activity}</td><td className="px-5 py-4"><StatusBadge value={`${course.completion_rate}%`} tone={course.completion_rate >= 70 ? "success" : "neutral"} /></td></tr>)}</tbody></AdminDataTable> : <div className="p-5"><EmptyState title="No course activity" description="Published course records will appear here when they have analytics data." /></div>}</Panel><Panel className="overflow-hidden"><div className="border-b border-line p-5"><h2 className="font-semibold">Challenge performance</h2><p className="mt-1 text-xs text-muted">Attempts and acceptance by difficulty.</p></div>{difficultyRows.length ? <div className="divide-y divide-line">{difficultyRows.map((row: any) => <div key={row.difficulty} className="flex items-center justify-between gap-4 p-4"><div><p className="font-medium capitalize">{row.difficulty}</p><p className="mt-1 text-xs text-muted">{row.attempts} attempts · {row.accepted} accepted</p></div><StatusBadge value={`${row.acceptance_rate}%`} /></div>)}</div> : <div className="p-5"><EmptyState title="No challenge attempts" description="Challenge statistics will appear when submissions are recorded." /></div>}<div className="border-t border-line p-5 text-sm"><div className="flex justify-between"><span className="text-muted">Total attempts</span><span>{data.challenges.attempts}</span></div><div className="mt-3 flex justify-between"><span className="text-muted">Accepted submissions</span><span>{data.challenges.accepted}</span></div><div className="mt-3 flex justify-between"><span className="text-muted">Acceptance rate</span><span>{data.challenges.success_rate}%</span></div></div></Panel></div>
      <Panel className="mt-6 p-5"><h2 className="font-semibold">Metric definitions</h2><div className="mt-4 grid gap-3 text-xs leading-5 text-muted sm:grid-cols-2"><p><strong className="text-foreground">Active learners:</strong> {definitions.active_students}</p><p><strong className="text-foreground">Completion rate:</strong> {definitions.completion_rate}</p><p><strong className="text-foreground">Challenge success:</strong> {definitions.challenge_success_rate}</p><p><strong className="text-foreground">Project submissions:</strong> {data.projects.definitions.submitted}</p></div></Panel>
    </>}
  </section>;
}
