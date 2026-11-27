"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, Clock, ListChecks, RefreshCw, Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ApiError, api, dashboardApi } from "@/lib/api";
import { roadmapApi } from "@/lib/roadmap-api";
import type { Dashboard, DashboardActivity, LearningPathEnrollment, User, WeeklyActivity } from "@/lib/types";
import { Card, Skeleton } from "@/components/ui";
import { useDashboardPreferences } from "@/components/student-dashboard-shell";

const clamp = (value: number) => Math.min(100, Math.max(0, Number.isFinite(value) ? value : 0));
const number = (value: number) => Number.isFinite(value) ? value.toLocaleString() : "0";

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [activity, setActivity] = useState<DashboardActivity[]>([]);
  const [weekly, setWeekly] = useState<WeeklyActivity | null>(null);
  const [learningPaths, setLearningPaths] = useState<LearningPathEnrollment[]>([]);
  const [error, setError] = useState("");
  const [hour, setHour] = useState<number | null>(null);
  const { language } = useDashboardPreferences();
  const load = () => {
    setError("");
    // Start optional dashboard panels at the same time as the required data.
    // They should not form a second network waterfall after the core cards.
    Promise.all([
      Promise.all([api.me(), api.dashboard()]),
      Promise.allSettled([dashboardApi.recentActivity(), dashboardApi.weeklyActivity(), roadmapApi.mine()]),
    ])
      .then(([[nextUser, nextData], results]) => {
        setUser(nextUser);
        setData(nextData);
        const [activityResult, weeklyResult, pathsResult] = results;
        if (activityResult.status === "fulfilled") setActivity(activityResult.value);
        else setActivity([]);
        if (weeklyResult.status === "fulfilled") setWeekly(weeklyResult.value);
        else setWeekly(null);
        if (pathsResult.status === "fulfilled") setLearningPaths(pathsResult.value);
        else setLearningPaths([]);
      })
      .catch(reason => {
        if (reason instanceof ApiError && reason.status === 401) { window.location.href = `/login?next=${encodeURIComponent("/dashboard")}`; return; }
        setError(reason instanceof Error ? reason.message : "Unable to load your dashboard.");
      });
  };
  useEffect(load, []);
  useEffect(() => { setHour(new Date().getHours()); }, []);

  if (error) return <div className="mx-auto max-w-3xl" role="alert"><Card className="border-red-400/20 bg-red-500/[.06] p-6"><div className="flex gap-3"><X className="shrink-0 text-red-300" /><div><h1 className="font-semibold text-red-100">{language === "my" ? "လေ့လာမှုဒေတာကို မဖတ်နိုင်ပါ" : "We couldn’t load your learning data"}</h1><p className="mt-2 text-sm leading-6 text-red-200/70">{error}</p><button type="button" onClick={load} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-red-400/15 px-4 py-2 text-sm font-semibold text-red-100"><RefreshCw size={16} /> Retry</button></div></div></Card></div>;
  if (!data || !user) return <DashboardSkeleton />;

  const firstName = user.full_name.trim().split(/\s+/)[0] || "Learner";
  const current = data.enrollments.find(item => item.progress_percent < 100) ?? data.enrollments[0];
  const completed = data.enrollments.filter(item => item.progress_percent >= 100).length;
  const inProgress = data.enrollments.filter(item => item.progress_percent > 0 && item.progress_percent < 100).length;
  const notStarted = data.enrollments.filter(item => item.progress_percent === 0).length;
  const greeting = hour == null ? "Good day" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const currentTarget = current ? (current.next_lesson_slug ?? current.last_lesson_slug ? `/courses/${current.course.slug}/learn/${current.next_lesson_slug ?? current.last_lesson_slug}` : `/courses/${current.course.slug}`) : "/courses";
  const metrics = [
    { label: "Enrolled courses", value: number(data.total_enrolled), icon: BookOpen, tone: "text-indigo-300", note: `${inProgress} in progress` },
    { label: "Completed lessons", value: number(data.completed_lessons), icon: ListChecks, tone: "text-emerald-300", note: "Verified completions" },
    { label: "Learning time", value: data.learning_time_minutes == null ? "—" : `${number(data.learning_time_minutes)} min`, icon: Clock, tone: "text-cyan-300", note: data.learning_time_minutes == null ? "Not tracked yet" : "Recorded time" },
    { label: "Certificates", value: number(data.certificates_earned), icon: Sparkles, tone: "text-amber-300", note: "Issued certificates" },
  ] as const;

  return <div className="mx-auto max-w-[1440px]">
    <div className="mb-7"><p className="text-xs font-semibold uppercase tracking-[.2em] text-indigo-300">Student dashboard</p><h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-50 sm:text-4xl">Welcome back, {firstName}</h1><p className="mt-2 text-sm text-slate-400">Stay consistent, learn with purpose, and keep building your momentum.</p></div>
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      <Card className="relative min-h-[252px] overflow-hidden border-indigo-300/20 bg-gradient-to-br from-[#6038d5] via-[#4f46c8] to-[#202b78] p-6 sm:p-8"><div className="pointer-events-none absolute -right-24 -top-28 h-72 w-72 rounded-full bg-violet-300/20 blur-3xl" /><div className="relative z-10 max-w-[56%] sm:max-w-[60%]"><p className="text-sm font-medium text-indigo-100">{greeting}, {firstName}.</p><h2 className="mt-3 text-2xl font-bold leading-tight text-white sm:text-3xl">Ready to continue your learning journey?</h2><p className="mt-3 text-sm leading-6 text-indigo-100/80">{current ? `Pick up ${current.course.title} where you left off.` : "Choose your first course and start learning today."}</p><div className="mt-6 flex flex-wrap gap-3"><Link href={currentTarget} className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-50">Continue learning <ArrowRight size={16} /></Link><Link href="/courses" className="inline-flex items-center gap-2 rounded-xl border border-white/25 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/15">Browse courses</Link></div></div><div className="absolute bottom-6 right-5 hidden h-36 w-48 rotate-[-3deg] rounded-xl border border-white/20 bg-[#111936]/80 p-3 shadow-2xl sm:block"><div className="flex gap-1.5"><span className="h-2 w-2 rounded-full bg-rose-300" /><span className="h-2 w-2 rounded-full bg-amber-300" /><span className="h-2 w-2 rounded-full bg-emerald-300" /></div><div className="mt-5 space-y-2 font-mono text-[10px]"><p><span className="text-violet-300">const</span> <span className="text-cyan-200">learn</span> = <span className="text-amber-200">true</span>;</p><p className="text-slate-400">{"// build your next idea"}</p><p><span className="text-violet-300">return</span> <span className="text-emerald-300">progress</span>;</p></div><div className="absolute -bottom-3 left-[-14px] right-[-14px] h-3 rounded-full bg-indigo-200/60" /></div></Card>
      <Card className="p-5 sm:p-6"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-slate-500">Your momentum</p><h2 className="mt-2 text-xl font-semibold">Learning streak</h2></div><span className="rounded-xl bg-orange-400/10 px-3 py-2 text-lg font-bold text-orange-300">{number(data.current_streak)}d</span></div><div className="mt-6 flex justify-between gap-2">{["M", "T", "W", "T", "F", "S", "S"].map((day, index) => <div className="text-center" key={`${day}-${index}`}><div className={`grid h-8 w-8 place-items-center rounded-full text-xs font-semibold ${index >= 7 - Math.min(data.current_streak, 7) ? "bg-indigo-500 text-white" : "bg-elevated text-slate-500"}`}>{day}</div></div>)}</div><div className="mt-6 border-t border-line/70 pt-5"><div className="flex items-center justify-between"><span className="text-sm font-medium">Daily lesson goal</span><span className="text-xs text-slate-500">Not configured</span></div><div className="mt-3 h-2 rounded-full bg-elevated"><div className="h-full w-0 rounded-full bg-gradient-to-r from-indigo-400 to-violet-400" /></div><Link href="/dashboard/study-plan" className="mt-4 inline-flex text-sm font-medium text-indigo-300 hover:text-white">Set a goal <ArrowRight className="ml-1" size={14} /></Link></div></Card>
    </div>
    <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]"><div className="grid grid-cols-2 gap-3 lg:grid-cols-4">{metrics.map(metric => <Card className="p-4 sm:p-5" key={metric.label}><div className="flex items-start justify-between gap-3"><p className="text-[11px] font-semibold uppercase tracking-[.12em] text-slate-500">{metric.label}</p><span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-white/[.04]"><metric.icon size={16} className={metric.tone} /></span></div><p className="mt-5 text-2xl font-bold tracking-tight text-slate-50">{metric.value}</p><p className="mt-1 text-xs text-slate-500">{metric.note}</p></Card>)}</div><Card className="p-5"><div className="flex items-center justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-slate-500">Insights</p><h2 className="mt-2 text-lg font-semibold">Recent activity</h2></div><ListChecks className="text-emerald-300" size={18} /></div>{activity.length ? <div className="mt-4 space-y-3">{activity.slice(0, 3).map((item, index) => <Link href={`/courses/${item.course_slug}`} className="flex gap-3 rounded-xl p-2 transition hover:bg-elevated" key={`${item.event_type}-${item.timestamp}-${index}`}><span className="mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-emerald-500/10 text-emerald-300"><ListChecks size={14} /></span><span className="min-w-0"><span className="block truncate text-sm font-medium">{item.title}</span><span className="mt-1 block truncate text-xs text-slate-500">{item.lesson_title ?? item.course_title}</span></span></Link>)}</div> : <p className="mt-5 rounded-xl bg-elevated p-3 text-xs leading-5 text-slate-500">Verified learning activity will appear here after your first lesson or quiz.</p>}</Card></div>
    <div className="mt-8 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]"><section><div className="mb-4 flex items-end justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-indigo-300">Keep going</p><h2 className="mt-1 text-xl font-semibold">Continue learning</h2></div><Link href="/dashboard/courses" className="text-sm font-medium text-indigo-300 hover:text-white">View all <ArrowRight className="ml-1 inline" size={14} /></Link></div>{data.enrollments.length ? <div className="grid gap-4 md:grid-cols-3">{data.enrollments.slice(0, 3).map((item, index) => <CourseCard item={item} variant={index} key={item.id} />)}</div> : <Card className="p-8 text-center"><BookOpen className="mx-auto text-slate-600" size={28} /><h3 className="mt-4 font-semibold">Your courses will appear here</h3><Link href="/courses" className="mt-4 inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold">Browse courses <ArrowRight size={15} /></Link></Card>}</section><Card className="p-5"><div className="flex items-center justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-slate-500">Plan ahead</p><h2 className="mt-1 text-lg font-semibold">Upcoming tasks</h2></div><Clock className="text-amber-300" size={18} /></div><div className="mt-5 rounded-xl bg-elevated p-4"><p className="text-sm font-medium text-slate-300">No upcoming tasks</p><p className="mt-1 text-xs leading-5 text-slate-500">Quizzes and project deadlines will appear here when they are assigned.</p></div><Link href="/dashboard/study-plan" className="mt-4 inline-flex text-sm font-medium text-indigo-300 hover:text-white">Open study planner <ArrowRight className="ml-1" size={14} /></Link></Card></div>
    <LearningPathsPanel items={learningPaths} />
    <div className="mt-8 grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(280px,.8fr)]"><WeeklyChart weekly={weekly} /><ProgressOverview enrolled={data.enrollments.length} completed={completed} inProgress={inProgress} notStarted={notStarted} /></div>
  </div>;
}

function LearningPathsPanel({ items }: { items: LearningPathEnrollment[] }) {
  return <section className="mt-8"><div className="mb-4 flex items-end justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.18em] text-indigo-300">My learning paths</p><h2 className="mt-1 text-xl font-semibold">Continue a roadmap</h2></div><Link href="/learning-paths" className="text-sm font-medium text-indigo-300 hover:text-white">Browse paths <ArrowRight className="ml-1 inline" size={14} /></Link></div>{items.length ? <div className="grid gap-4 md:grid-cols-3">{items.slice(0, 3).map(item => <Card className="p-5" key={item.id}><div className="flex items-center justify-between gap-3"><h3 className="truncate font-semibold">{item.roadmap_title ?? item.roadmap_slug}</h3><span className="text-xs text-indigo-300">{Math.round(item.progress.progress_percent)}%</span></div><div className="mt-4 h-2 rounded-full bg-elevated"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-400" style={{ width: `${Math.min(100, Math.max(0, item.progress.progress_percent))}%` }} /></div><p className="mt-3 text-xs text-slate-500">{item.progress.completed_steps}/{item.progress.total_steps} verified steps</p><Link href={item.progress.resume?.href ?? `/learning-paths/${item.roadmap_slug}`} className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-indigo-300 hover:text-white">{item.progress.resume ? "Resume path" : "Open path"} <ArrowRight size={14} /></Link></Card>)}</div> : <Card className="p-6"><p className="text-sm text-slate-400">You have not joined a learning path yet.</p><Link href="/learning-paths" className="mt-4 inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold">Explore learning paths <ArrowRight size={15} /></Link></Card>}</section>;
}

function CourseCard({ item, variant }: { item: Dashboard["enrollments"][number]; variant: number }) {
  const progress = clamp(item.progress_percent);
  const targetSlug = item.next_lesson_slug ?? item.last_lesson_slug;
  const target = targetSlug ? `/courses/${item.course.slug}/learn/${targetSlug}` : `/courses/${item.course.slug}`;
  const gradients = ["from-indigo-500/25 to-violet-500/5", "from-cyan-500/20 to-indigo-500/5", "from-fuchsia-500/20 to-indigo-500/5"];
  return <Card className="overflow-hidden transition hover:-translate-y-0.5 hover:border-indigo-400/30"><div className={`h-20 bg-gradient-to-br ${gradients[variant % gradients.length]} p-4`}><div className="grid h-10 w-10 place-items-center rounded-xl bg-surface/80 text-indigo-200"><BookOpen size={19} /></div></div><div className="p-4"><p className="text-[10px] font-semibold uppercase tracking-[.14em] text-slate-500">{item.course.language.name}</p><h3 className="mt-1 line-clamp-2 min-h-[42px] font-semibold">{item.course.title}</h3><div className="mt-4 flex items-center justify-between text-xs text-slate-500"><span>{item.completed_lessons}/{item.total_lessons} lessons</span><span className="font-semibold text-indigo-300">{Math.round(progress)}%</span></div><div className="mt-2 h-1.5 rounded-full bg-elevated"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-400" style={{ width: `${progress}%` }} /></div><Link href={target} className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-indigo-300 hover:text-white">{progress >= 100 ? "Review course" : "Resume learning"} <ArrowRight size={14} /></Link></div></Card>;
}

function WeeklyChart({ weekly }: { weekly: WeeklyActivity | null }) {
  return <Card className="p-5 sm:p-6"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-indigo-300">Analytics</p><h2 className="mt-1 text-lg font-semibold">Weekly learning activity</h2><p className="mt-1 text-xs text-slate-500">Verified lessons and quizzes across the last seven days.</p></div><ListChecks className="text-indigo-300" size={18} /></div>{weekly ? <div className="mt-7 grid grid-cols-7 items-end gap-2 sm:gap-4" aria-label="Weekly verified learning activity">{weekly.days.map(day => { const total = day.completed_lessons + day.quiz_attempts; const height = total ? Math.min(100, 18 + total * 18) : 0; return <div className="flex min-w-0 flex-col items-center gap-2" key={day.date}><div className="flex h-32 w-full items-end rounded-xl bg-elevated/70 p-1.5"><div className="w-full rounded-lg bg-gradient-to-t from-indigo-600 to-violet-300 transition-all" style={{ height: `${height}%` }} title={`${day.completed_lessons} lessons, ${day.quiz_attempts} quizzes`} /></div><span className="text-[10px] text-slate-500">{new Date(`${day.date}T00:00:00`).toLocaleDateString(undefined, { weekday: "short" }).slice(0, 3)}</span></div> })}</div> : <Skeleton className="mt-6 h-32" />} {!weekly?.learning_time_available && <p className="mt-5 text-xs text-slate-600">Learning duration is not tracked yet; the chart shows verified learning events.</p>}</Card>;
}

function ProgressOverview({ enrolled, completed, inProgress, notStarted }: { enrolled: number; completed: number; inProgress: number; notStarted: number }) {
  const completeDegrees = enrolled ? completed / enrolled * 360 : 0;
  const progressDegrees = enrolled ? (completed + inProgress) / enrolled * 360 : 0;
  const style = { background: enrolled ? `conic-gradient(#10B981 0deg ${completeDegrees}deg, #6366F1 ${completeDegrees}deg ${progressDegrees}deg, #334155 ${progressDegrees}deg 360deg)` : "#26334f" };
  return <Card className="p-5 sm:p-6"><p className="text-xs font-semibold uppercase tracking-[.16em] text-indigo-300">Overview</p><h2 className="mt-1 text-lg font-semibold">Course progress</h2><div className="mt-6 flex items-center gap-6"><div className="grid h-32 w-32 shrink-0 place-items-center rounded-full" style={style}><div className="grid h-20 w-20 place-items-center rounded-full bg-surface"><span className="text-xl font-bold">{enrolled ? `${Math.round((completed + inProgress) / enrolled * 100)}%` : "—"}</span></div></div><div className="space-y-3 text-sm"><Legend color="bg-emerald-400" label="Completed" value={completed} /><Legend color="bg-indigo-400" label="In progress" value={inProgress} /><Legend color="bg-slate-600" label="Not started" value={notStarted} /></div></div></Card>;
}

function Legend({ color, label, value }: { color: string; label: string; value: number }) { return <div className="flex items-center gap-2"><span className={`h-2.5 w-2.5 rounded-full ${color}`} /><span className="text-slate-400">{label}</span><span className="ml-auto font-semibold text-slate-200">{value}</span></div>; }
function DashboardSkeleton() { return <div className="mx-auto max-w-[1440px]"><Skeleton className="h-10 w-80" /><Skeleton className="mt-3 h-5 w-[28rem] max-w-full" /><div className="mt-7 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]"><Skeleton className="h-64" /><Skeleton className="h-64" /></div><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{Array.from({ length: 4 }).map((_, index) => <Skeleton className="h-32" key={index} />)}</div><div className="mt-8 grid gap-5 lg:grid-cols-3">{Array.from({ length: 3 }).map((_, index) => <Skeleton className="h-56" key={index} />)}</div></div>; }
