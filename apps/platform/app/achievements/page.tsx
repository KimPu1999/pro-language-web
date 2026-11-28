"use client";

import Link from "next/link";
import { Award, BookOpen, CheckCircle2, Clock3, Code2, GraduationCap, Layers3, LockKeyhole, ShieldCheck, Sparkles, Trophy } from "lucide-react";
import { useEffect, useMemo, useState, type ComponentType } from "react";

type Item = { id: string; code: string; title: string; description: string; criteria: string; category: string; badge_image_url?: string | null; icon_name?: string; tier: string; state: string; progress: { current: number | null; target: number; remaining: number | null; available: boolean; unavailable_reason?: string | null }; award?: { award_id: string; awarded_at: string; status: string } | null };
type Result = { metrics: { published_definitions: number; earned_badges: number; eligible_badges: number; in_progress_badges: number; recent_awards: unknown[] }; items: Item[]; source: string };

const iconMap: Record<string, ComponentType<{ size?: number; className?: string }>> = { Award, BookOpen, Code2, GraduationCap, Layers3, Sparkles, Trophy };
const safeBadgeImage = (value?: string | null) => value && value.startsWith("/") && /\.(png|jpe?g|webp)(\?.*)?$/i.test(value) ? value : null;

function BadgeIcon({ item, size = 28 }: { item: Item; size?: number }) {
  const Icon = iconMap[item.icon_name || "Award"] || Award;
  const image = safeBadgeImage(item.badge_image_url);
  return image ? <img src={image} alt="" width={size + 10} height={size + 10} className="h-12 w-12 object-contain" /> : <Icon size={size} aria-hidden="true" />;
}

export default function AchievementsPage() {
  const [data, setData] = useState<Result | null>(null);
  const [category, setCategory] = useState("all");
  const [state, setState] = useState("loading");
  useEffect(() => { fetch("/api/v1/me/achievements", { credentials: "include", cache: "no-store" }).then(response => response.ok ? response.json() : Promise.reject(new Error("Unable to load achievements."))).then(value => { setData(value); setState("ready"); }).catch(() => setState("error")); }, []);
  const items = useMemo(() => (data?.items ?? []).filter(item => category === "all" || item.category === category), [category, data]);
  const earned = items.filter(item => item.state === "earned");
  const available = items.filter(item => item.state !== "earned");

  if (state === "loading") return <section className="mx-auto max-w-6xl px-5 py-12 sm:px-6"><div className="rounded-2xl border border-line bg-surface p-8 text-sm text-muted">Loading verified achievements…</div></section>;
  if (state === "error") return <section className="mx-auto max-w-6xl px-5 py-12 sm:px-6"><div role="alert" className="rounded-2xl border border-red-500/25 bg-red-500/10 p-6 text-sm text-red-700 dark:text-red-200">Unable to load achievements. Please try again later.</div></section>;
  const metrics: { label: string; value: number; Icon: ComponentType<any> }[] = [["Published definitions", data?.metrics.published_definitions ?? 0, Award], ["Earned badges", data?.metrics.earned_badges ?? 0, Trophy], ["Eligible", data?.metrics.eligible_badges ?? 0, CheckCircle2], ["In progress", data?.metrics.in_progress_badges ?? 0, Clock3]].map(([label, value, Icon]) => ({ label: label as string, value: value as number, Icon: Icon as ComponentType<any> }));

  return <section className="mx-auto max-w-6xl px-5 py-10 sm:px-6 sm:py-14">
    <div className="rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/15 via-surface to-surface p-6 sm:p-10">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[.18em] text-primary"><ShieldCheck size={16} aria-hidden="true" /> Verified Learning</div>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-5"><div><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Achievements & Badges</h1><p className="mt-3 max-w-2xl leading-7 text-muted">Badges are awarded from verified platform records, not client-side claims.</p></div><Link href="/courses" className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-hover">Continue learning <BookOpen size={16} /></Link></div>
    </div>

    <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{metrics.map(({ label, value, Icon }) => <div key={label} className="rounded-2xl border border-line bg-surface p-5"><Icon size={18} className="text-primary" aria-hidden="true" /><p className="mt-4 text-2xl font-bold">{value}</p><p className="mt-1 text-sm text-muted">{label}</p></div>)}</div>

    {!data?.items.length ? <div className="mt-8 rounded-2xl border border-dashed border-line bg-surface p-10 text-center"><Award className="mx-auto text-muted" size={34} aria-hidden="true" /><h2 className="mt-4 text-xl font-semibold">No achievement definitions are published yet.</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">Verified rewards will appear here when the academy publishes them.</p></div> : <>
      <div className="mt-8 flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-semibold">My badge library</h2><p className="mt-1 text-sm text-muted">Earned, eligible, and in-progress achievements from persisted learning records.</p></div><label className="text-sm text-muted">Category <select value={category} onChange={event => setCategory(event.target.value)} className="ml-2 rounded-xl border border-line bg-surface px-3 py-2 text-foreground"><option value="all">All categories</option>{[...new Set((data.items ?? []).map(item => item.category))].map(value => <option key={value} value={value}>{value}</option>)}</select></label></div>
      <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{earned.map(item => <BadgeCard key={item.id} item={item} />)}</div>
      {!earned.length && <div className="mt-5 rounded-2xl border border-line bg-surface p-6 text-sm text-muted">No badges earned yet. Complete a published requirement to receive a verified award.</div>}
      <h2 className="mt-10 text-xl font-semibold">Available achievements</h2><div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{available.map(item => <BadgeCard key={item.id} item={item} />)}</div>
    </>}
  </section>;
}

function BadgeCard({ item }: { item: Item }) {
  const earned = item.state === "earned";
  const eligible = item.state === "eligible";
  const locked = item.state === "not_started" || item.state === "unavailable";
  return <article className={`rounded-2xl border bg-surface p-5 transition hover:border-primary/60 ${earned ? "border-primary/40" : "border-line"}`}><div className="flex items-start justify-between gap-3"><div className={`grid h-14 w-14 place-items-center rounded-2xl ${earned ? "bg-primary/15 text-primary" : "bg-ink text-muted"}`}><BadgeIcon item={item} /></div><span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold ${earned ? "bg-emerald-500/12 text-emerald-700 dark:text-emerald-200" : eligible ? "bg-primary/12 text-primary" : "bg-ink text-muted"}`}>{earned ? <CheckCircle2 size={13} /> : locked ? <LockKeyhole size={13} /> : <Clock3 size={13} />} {earned ? "Earned" : item.state.replaceAll("_", " ")}</span></div><h3 className="mt-5 font-semibold">{item.title}</h3><p className="mt-2 line-clamp-3 text-sm leading-6 text-muted">{item.description}</p>{!earned && item.progress.available && <div className="mt-4"><div className="flex justify-between text-xs text-muted"><span>{item.progress.current ?? 0} of {item.progress.target} verified</span><span>{item.progress.remaining ?? 0} remaining</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink"><div className="h-full rounded-full bg-primary" style={{ width: `${Math.min(100, ((item.progress.current ?? 0) / Math.max(1, item.progress.target)) * 100)}%` }} /></div></div>}{item.award && <p className="mt-4 text-xs text-muted">Awarded {new Date(item.award.awarded_at).toLocaleDateString()}</p>}{item.state === "unavailable" && <p className="mt-4 text-xs text-amber-700 dark:text-amber-200">{item.progress.unavailable_reason}</p>}<Link href={`/achievements/${item.code}`} className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary-hover">View details <Sparkles size={14} /></Link></article>;
}
