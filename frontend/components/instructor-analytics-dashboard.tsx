"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, RefreshCw, Search, Users } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { analyticsApi, InstructorCourse, InstructorKpis, InstructorOverview, InstructorReviews, InstructorRow, InstructorTrend } from "@/lib/analytics-api";
import { Badge, Button, Card, Skeleton } from "./ui";

const initialRange = () => {
  const end = new Date();
  const start = new Date(end.getTime() - 29 * 86400000);
  return { start: start.toISOString().slice(0, 10), end: end.toISOString().slice(0, 10) };
};

const kpiKeys: (keyof InstructorKpis)[] = ["total_instructors", "active_instructors", "published_courses", "new_enrollments", "active_learners", "course_completions", "lessons_published", "project_reviews_completed", "pending_project_reviews"];

export function InstructorAnalyticsDashboard() {
  const { locale } = useI18n();
  const copy = locale === "my" ? {
    eyebrow: "ပလက်ဖောင်း အချက်အလက်",
    title: "သင်ကြားသူများ၏ ခွဲခြမ်းစိတ်ဖြာမှု",
    description: "ရွေးချယ်ထားသော UTC အချိန်ကာလအတွင်း PostgreSQL မှရရှိသော အမှန်တကယ်မှတ်တမ်းများကို ပြသထားသည်။",
    from: "စတင်ချိန်", to: "ပြီးဆုံးချိန်", apply: "စစ်ထုတ်ရန်", refresh: "ပြန်လည်ရယူရန်", export: "CSV ထုတ်ရန်",
    overview: "အနှစ်ချုပ်", performance: "သင်ကြားသူ စွမ်းဆောင်ရည်", courses: "သင်တန်း စွမ်းဆောင်ရည်", reviews: "Project review များ", trends: "လုပ်ဆောင်ချက် လမ်းကြောင်း",
    search: "သင်ကြားသူအမည် သို့မဟုတ် အီးမေးလ်ရှာရန်", status: "အခြေအနေ", all: "အားလုံး", active: "လှုပ်ရှားနေသည်", inactive: "လုပ်ဆောင်ချက် မရှိသေးပါ",
    instructor: "သင်ကြားသူ", associatedCourses: "ချိတ်ဆက်သင်တန်း", publishedLessons: "ထုတ်ဝေပြီးသင်ခန်းစာ", learners: "လေ့လာသူများ", completions: "ပြီးမြောက်မှု", reviewsCompleted: "ပြီးမြောက်သည့် review", lastActivity: "နောက်ဆုံးလုပ်ဆောင်ချက်", actions: "လုပ်ဆောင်ချက်", view: "အသေးစိတ်ကြည့်ရန်",
    noData: "ဤကာလအတွက် မှတ်တမ်းမရှိသေးပါ။", unavailable: "ဤ data source ကို မရရှိနိုင်သေးပါ။", loading: "ဒေတာရယူနေသည်…", retry: "ပြန်စမ်းရန်", pageSize: "စာမျက်နှာအရွယ်", previous: "နောက်သို့", next: "ရှေ့သို့", course: "သင်တန်း", published: "ထုတ်ဝေပြီး", enrolled: "စာရင်းသွင်းသူများ", newEnrollments: "စာရင်းသွင်းမှုအသစ်", activeLearners: "လှုပ်ရှားသည့်လေ့လာသူများ", projectReviews: "Project reviews", turnaround: "Review ကြာချိန်", submittedProjects: "တင်ထားသော projects", pendingReviews: "စောင့်ဆိုင်းနေသော reviews", feedback: "Feedback ပြည့်စုံမှု", noActivity: "လုပ်ဆောင်ချက် မမှတ်တမ်းတင်ရသေးပါ။", source: "Data source", updated: "နောက်ဆုံးပြင်ဆင်ချိန်", details: "Metric အဓိပ္ပါယ်ဖွင့်ဆိုချက်",
  } : {
    eyebrow: "Platform intelligence", title: "Instructor analytics", description: "Real PostgreSQL records for the selected UTC reporting period.", from: "From", to: "To", apply: "Apply", refresh: "Refresh", export: "Export CSV",
    overview: "Overview", performance: "Instructor performance", courses: "Course performance", reviews: "Project reviews", trends: "Activity trends", search: "Search instructor or email", status: "Status", all: "All", active: "Active", inactive: "No activity",
    instructor: "Instructor", associatedCourses: "Associated courses", publishedLessons: "Published lessons", learners: "Learners", completions: "Completions", reviewsCompleted: "Completed reviews", lastActivity: "Last activity", actions: "Actions", view: "View details", noData: "No records were recorded for this period.", unavailable: "This data source is not available.", loading: "Loading analytics…", retry: "Retry", pageSize: "Rows", previous: "Previous", next: "Next", course: "Course", published: "Published", enrolled: "Enrolled learners", newEnrollments: "New enrollments", activeLearners: "Active learners", projectReviews: "Project reviews", turnaround: "Review turnaround", submittedProjects: "Submitted projects", pendingReviews: "Pending reviews", feedback: "Feedback completed", noActivity: "No activity has been recorded.", source: "Data source", updated: "Updated", details: "Metric definitions",
  };
  const kpiLabels: Record<keyof InstructorKpis, string> = locale === "my" ? { total_instructors: "သင်ကြားသူ စုစုပေါင်း", active_instructors: "လှုပ်ရှားနေသော သင်ကြားသူများ", published_courses: "ထုတ်ဝေပြီးသင်တန်းများ", new_enrollments: "စာရင်းသွင်းမှုအသစ်", active_learners: "လှုပ်ရှားသည့်လေ့လာသူများ", course_completions: "သင်တန်းပြီးမြောက်မှု", lessons_published: "ထုတ်ဝေပြီးသင်ခန်းစာများ", project_reviews_completed: "ပြီးမြောက်သည့် Project review များ", pending_project_reviews: "စောင့်ဆိုင်းနေသော Project review များ" } : { total_instructors: "Total instructors", active_instructors: "Active instructors", published_courses: "Published courses", new_enrollments: "New enrollments", active_learners: "Active learners", course_completions: "Course completions", lessons_published: "Lessons published", project_reviews_completed: "Project reviews completed", pending_project_reviews: "Pending project reviews" };
  const range = useMemo(initialRange, []);
  const [start, setStart] = useState(range.start);
  const [end, setEnd] = useState(range.end);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [courseId, setCourseId] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [kpis, setKpis] = useState<InstructorKpis | null>(null);
  const [comparison, setComparison] = useState<InstructorOverview["comparison"]>(null);
  const [rows, setRows] = useState<InstructorRow[]>([]);
  const [courses, setCourses] = useState<InstructorCourse[]>([]);
  const [courseOptions, setCourseOptions] = useState<InstructorCourse[]>([]);
  const [reviews, setReviews] = useState<InstructorReviews | null>(null);
  const [trends, setTrends] = useState<InstructorTrend[]>([]);
  const [definitions, setDefinitions] = useState<Record<string, string>>({});
  const [sources, setSources] = useState<Record<string, string>>({});
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [selected, setSelected] = useState<InstructorRow | null>(null);
  const [detailCourses, setDetailCourses] = useState<{ id: string; title: string; slug: string; published: boolean }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  const load = () => {
    setLoading(true); setError("");
    Promise.all([
      analyticsApi.instructorOverview(start, end, { course_id: courseId }),
      analyticsApi.instructorList(start, end, { search, status, course_id: courseId, page, page_size: pageSize, sort: "activity_desc" }),
      analyticsApi.instructorTrends(start, end, { bucket: "daily", course_id: courseId }),
      analyticsApi.instructorCourses(start, end, { course_id: courseId, page: 1, page_size: 10 }),
      analyticsApi.instructorReviews(start, end),
    ]).then(([overview, list, trend, courseData, reviewData]) => {
      setKpis(overview.kpis); setComparison(overview.comparison); setDefinitions(overview.definitions); setSources(overview.sources); setRows(list.items); setTotal(list.total); setPages(list.pages); setTrends(trend.items); setCourses(courseData.items); if (!courseId) setCourseOptions(courseData.items); setReviews(reviewData);
    }).catch((cause) => setError(cause instanceof Error ? cause.message : "Unable to load instructor analytics")).finally(() => setLoading(false));
  };

  useEffect(() => { if (start && end) load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [start, end, page, pageSize, status, courseId]);

  const searchNow = () => { setPage(1); load(); };
  const exportCsv = async () => {
    setExporting(true); setError("");
    try { const blob = await analyticsApi.exportInstructors(start, end, { search, status }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = `instructor-analytics-${start}.csv`; link.click(); URL.revokeObjectURL(url); } catch (cause) { setError(cause instanceof Error ? cause.message : "Export failed"); } finally { setExporting(false); }
  };
  const openDetail = async (row: InstructorRow) => {
    setSelected(row); setDetailCourses([]);
    try { const detail = await analyticsApi.instructorDetail(row.id, start, end); setDetailCourses(detail.courses); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to load instructor details"); }
  };
  const maxTrend = Math.max(...trends.map((item) => item.activity), 1);

  return <section className="space-y-6">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-indigo-300">{copy.eyebrow}</p><h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">{copy.title}</h1><p className="mt-2 max-w-3xl text-sm text-slate-400">{copy.description}</p></div><div className="flex flex-wrap gap-2"><Button className="bg-elevated" onClick={load} disabled={loading}><RefreshCw size={16} className="mr-2 inline" />{copy.refresh}</Button><Button onClick={exportCsv} disabled={exporting}><Download size={16} className="mr-2 inline" />{exporting ? "Preparing…" : copy.export}</Button></div></div>
    <Card className="sticky top-2 z-10 flex flex-wrap items-end gap-3 p-4"><label className="text-xs text-slate-400">{copy.from}<input type="date" value={start} max={end} onChange={(event) => setStart(event.target.value)} className="mt-1 block rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white" /></label><label className="text-xs text-slate-400">{copy.to}<input type="date" value={end} min={start} onChange={(event) => setEnd(event.target.value)} className="mt-1 block rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white" /></label><label className="text-xs text-slate-400">{copy.course}<select value={courseId} onChange={(event) => { setCourseId(event.target.value); setPage(1); }} className="mt-1 block max-w-[240px] rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white"><option value="">{copy.all}</option>{courseOptions.map((course) => <option value={course.id} key={course.id}>{course.title}</option>)}</select></label><Button onClick={load}>{copy.apply}</Button><span className="ml-auto text-xs text-slate-500">UTC · {start} → {end}</span></Card>
    {error && <Card className="border-red-400/30 p-5 text-sm text-red-200" role="alert"><span>{error}</span><button className="ml-3 underline" onClick={load}>{copy.retry}</button></Card>}
    {loading ? <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{kpiKeys.map((key) => <Skeleton className="h-28" key={key} />)}</div> : kpis ? <>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{kpiKeys.map((key) => <Card className="p-5" key={key}><p className="text-sm text-slate-400">{kpiLabels[key]}</p><p className="mt-3 text-3xl font-bold">{kpis[key].toLocaleString()}</p><p className="mt-2 text-xs text-slate-500">{definitions[key] || copy.source}</p></Card>)}</div>
      {comparison && <Card className="p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold">{locale === "my" ? "ယခင်ကာလနှင့် နှိုင်းယှဉ်မှု" : "Previous equivalent period"}</h2><p className="mt-1 text-xs text-slate-500">{locale === "my" ? "အချိန်ကာလတူ အချက်အလက်အပေါ် အခြေခံထားသည်။" : "Compared with the matched duration immediately before the selected period."}</p></div><div className="grid grid-cols-2 gap-3 sm:grid-cols-4">{Object.entries(comparison).map(([key, item]) => <div className="rounded-lg bg-elevated px-3 py-2" key={key}><p className="text-[11px] capitalize text-slate-500">{key.replaceAll("_", " ")}</p><p className="mt-1 text-sm font-semibold">{item.difference >= 0 ? "+" : ""}{item.difference.toLocaleString()}</p><p className="text-[11px] text-slate-500">{item.percentage == null ? "N/A" : `${item.percentage}%`}</p></div>)}</div></div></Card>}
      <div className="grid gap-5 xl:grid-cols-[1.3fr_.7fr]"><Card className="p-5"><div className="flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold">{copy.trends}</h2><p className="mt-1 text-xs text-slate-500">{copy.description}</p></div><Users size={18} className="text-indigo-300" /></div><div className="mt-6 flex h-56 items-end gap-1.5 overflow-x-auto">{trends.map((item) => <div className="group flex min-w-[20px] flex-1 flex-col items-center justify-end gap-2" key={item.date}><div className="w-full rounded-t bg-gradient-to-t from-indigo-600 to-violet-300" title={`${item.date}: ${item.activity}`} style={{ height: `${item.activity ? Math.max(8, item.activity / maxTrend * 100) : 3}%` }} /><span className="w-full truncate text-center text-[10px] text-slate-600">{item.date.slice(5)}</span></div>)}</div></Card><Card className="p-5"><h2 className="text-lg font-semibold">{copy.reviews}</h2>{reviews && <div className="mt-4 grid grid-cols-2 gap-3 text-sm"><Metric label={copy.submittedProjects} value={reviews.submitted_projects} /><Metric label={copy.pendingReviews} value={reviews.pending_reviews} /><Metric label={copy.feedback} value={reviews.feedback_completed} /><Metric label={copy.turnaround} value={reviews.median_turnaround_hours == null ? "N/A" : `${reviews.median_turnaround_hours}h`} /></div>}<p className="mt-5 text-xs text-slate-500">{definitions.project_reviews_completed}</p></Card></div>
      <Card className="overflow-hidden"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-5"><div><h2 className="text-lg font-semibold">{copy.performance}</h2><p className="mt-1 text-sm text-slate-500">{total.toLocaleString()} {copy.instructor.toLowerCase()} records · {sources.instructors || copy.unavailable}</p></div><div className="flex flex-wrap gap-2"><div className="relative"><Search size={15} className="absolute left-3 top-3 text-slate-500" /><input value={search} onChange={(event) => setSearch(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") searchNow(); }} placeholder={copy.search} className="w-56 rounded-lg border border-line bg-ink py-2 pl-9 pr-3 text-sm" /></div><select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm"><option value="">{copy.all}</option><option value="active">{copy.active}</option><option value="inactive">{copy.inactive}</option></select></div></div><div className="overflow-x-auto"><table className="min-w-[900px] w-full text-left text-sm"><thead className="border-b border-line text-xs text-slate-500"><tr>{[copy.instructor, copy.associatedCourses, copy.publishedLessons, copy.learners, copy.completions, copy.reviewsCompleted, copy.lastActivity, copy.actions].map((heading) => <th className="px-5 py-3 font-medium" key={heading}>{heading}</th>)}</tr></thead><tbody>{rows.map((row) => <tr className="border-b border-line/60" key={row.id}><td className="px-5 py-4"><p className="font-medium">{row.display_name}</p>{row.email && <p className="mt-1 text-xs text-slate-500">{row.email}</p>}<Badge className="mt-2">{row.activity_state === "available" ? copy.active : copy.inactive}</Badge></td><td className="px-5 py-4">{row.associated_courses}</td><td className="px-5 py-4">{row.published_lessons}</td><td className="px-5 py-4">{row.active_learners}</td><td className="px-5 py-4">{row.course_completions}</td><td className="px-5 py-4">{row.completed_reviews}</td><td className="px-5 py-4 text-xs text-slate-400">{row.last_recorded_activity ? new Date(row.last_recorded_activity).toLocaleString() : "—"}</td><td className="px-5 py-4"><button className="text-indigo-300 hover:text-indigo-200" onClick={() => void openDetail(row)}>{copy.view}</button></td></tr>)}</tbody></table></div>{!rows.length && <p className="p-8 text-center text-sm text-slate-500">{total ? copy.unavailable : copy.noData}</p>}<div className="flex flex-wrap items-center justify-between gap-3 border-t border-line p-4 text-xs text-slate-500"><label>{copy.pageSize}<select value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }} className="ml-2 rounded border border-line bg-ink px-2 py-1"><option value={10}>10</option><option value={25}>25</option><option value={50}>50</option></select></label><div className="flex items-center gap-2"><button disabled={page <= 1} onClick={() => setPage((value) => value - 1)} className="rounded border border-line px-3 py-1 disabled:opacity-40">{copy.previous}</button><span>{page} / {Math.max(1, pages)}</span><button disabled={!pages || page >= pages} onClick={() => setPage((value) => value + 1)} className="rounded border border-line px-3 py-1 disabled:opacity-40">{copy.next}</button></div></div></Card>
      <div className="grid gap-5 lg:grid-cols-2"><Card className="overflow-hidden"><div className="border-b border-line p-5"><h2 className="font-semibold">{copy.courses}</h2></div><div className="overflow-x-auto"><table className="min-w-[700px] w-full text-left text-sm"><thead className="border-b border-line text-xs text-slate-500"><tr>{[copy.course, copy.publishedLessons, copy.enrolled, copy.newEnrollments, copy.activeLearners, copy.completions].map((heading) => <th className="px-4 py-3 font-medium" key={heading}>{heading}</th>)}</tr></thead><tbody>{courses.map((course) => <tr className="border-b border-line/60" key={course.id}><td className="px-4 py-3 font-medium">{course.title}</td><td className="px-4 py-3">{course.published_lessons}</td><td className="px-4 py-3">{course.enrolled_learners}</td><td className="px-4 py-3">{course.new_enrollments}</td><td className="px-4 py-3">{course.active_learners}</td><td className="px-4 py-3">{course.course_completions}</td></tr>)}</tbody></table></div>{!courses.length && <p className="p-6 text-sm text-slate-500">{copy.noData}</p>}</Card><Card className="p-5"><h2 className="font-semibold">{copy.details}</h2><div className="mt-4 space-y-4 text-sm text-slate-400">{Object.entries(definitions).slice(0, 8).map(([key, value]) => <div key={key}><Badge>{key.replaceAll("_", " ")}</Badge><p className="mt-2 leading-6">{value}</p></div>)}</div></Card></div>
    </> : <Card className="p-8 text-sm text-slate-500">{copy.unavailable}</Card>}
    {selected && <div className="fixed inset-0 z-30 flex items-end justify-center bg-black/60 p-4 sm:items-center" role="dialog" aria-modal="true"><Card className="max-h-[85vh] w-full max-w-2xl overflow-y-auto p-6"><div className="flex items-start justify-between gap-4"><div><p className="text-sm text-indigo-300">{copy.instructor}</p><h2 className="mt-1 text-2xl font-bold">{selected.display_name}</h2><p className="mt-1 text-sm text-slate-500">{selected.email || copy.unavailable}</p></div><button aria-label="Close" className="text-slate-400" onClick={() => setSelected(null)}>×</button></div><div className="mt-6 grid gap-3 sm:grid-cols-3"><Metric label={copy.associatedCourses} value={selected.associated_courses} /><Metric label={copy.activeLearners} value={selected.active_learners} /><Metric label={copy.completions} value={selected.course_completions} /></div><h3 className="mt-7 font-semibold">{copy.courses}</h3><div className="mt-3 space-y-2">{detailCourses.map((course) => <div className="flex items-center justify-between rounded-lg bg-elevated p-3 text-sm" key={course.id}><span>{course.title}</span><Badge>{course.published ? copy.published : "Draft"}</Badge></div>)}{!detailCourses.length && <p className="text-sm text-slate-500">{copy.noData}</p>}</div></Card></div>}
  </section>;
}

function Metric({ label, value }: { label: string; value: string|number }) { return <div className="rounded-lg bg-elevated p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-lg font-semibold">{typeof value === "number" ? value.toLocaleString() : value}</p></div>; }
