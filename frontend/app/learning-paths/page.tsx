"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { roadmapApi } from "@/lib/roadmap-api";
import type { LearningPathEnrollment, Roadmap } from "@/lib/types";
import { useI18n } from "@/lib/i18n";
import { Badge, Card, Skeleton } from "@/components/ui";

export default function LearningPathsPage() {
  const { locale } = useI18n();
  const my = locale === "my";
  const [items, setItems] = useState<Roadmap[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [mine, setMine] = useState<LearningPathEnrollment[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [level, setLevel] = useState("");
  const [duration, setDuration] = useState("");
  const [technology, setTechnology] = useState("");
  const [sort, setSort] = useState("title");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    roadmapApi.categories().then(setCategories).catch(() => setCategories([]));
    roadmapApi.mine().then(setMine).catch(() => setMine([]));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      const params = new URLSearchParams({ page: String(page), page_size: "12", sort, locale });
      if (query.trim()) params.set("search", query.trim());
      if (category) params.set("career_category", category);
      if (level) params.set("difficulty", level);
      if (duration) params.set("duration", duration);
      if (technology.trim()) params.set("technology", technology.trim());
      roadmapApi.list(`?${params}`).then(result => {
        setItems(result.items); setPages(result.pages); setTotal(result.total); setError("");
      }).catch(reason => setError(reason instanceof Error ? reason.message : "Unable to load learning paths"))
        .finally(() => setLoading(false));
    }, 180);
    return () => clearTimeout(timer);
  }, [query, category, level, duration, technology, sort, page, locale, reload]);

  const active = useMemo(() => new Map(mine.map(item => [item.roadmap_id, item])), [mine]);
  const featured = items.slice(0, 3);
  const hasFilters = Boolean(query || category || level || duration || technology || sort !== "title");
  const allItems = !hasFilters && page === 1 ? items.slice(3) : items;
  const reset = () => { setQuery(""); setCategory(""); setLevel(""); setDuration(""); setTechnology(""); setSort("title"); setPage(1); };

  return <section className="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <div className="rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-500/20 via-surface to-surface p-8 sm:p-12"><div className="max-w-3xl"><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">{my ? "ပညာရပ်တိုးတက်ရေး လမ်းကြောင်းများ" : "Free professional learning journeys"}</p><h1 className="mt-4 text-4xl font-extrabold tracking-tight sm:text-6xl">{my ? "စူးစမ်းသူမှ ကျွမ်းကျင်သူအထိ ရှင်းလင်းသောလမ်းကြောင်း။" : "A clear route from curious to capable."}</h1><p className="mt-5 text-lg leading-8 text-slate-300">{my ? "အခြေခံမှ professional practice အထိ စစ်ဆေးအတည်ပြုထားသော အဆင့်များနှင့် လက်တွေ့သင်တန်းများကို လေ့လာပါ။" : "Follow reviewed stages from fundamentals to professional practice, using real courses and verified progress from your account."}</p></div></div>
    <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><div className="relative sm:col-span-2"><Search className="absolute left-4 top-3.5 text-slate-500" size={19} /><input aria-label="Search learning paths" value={query} onChange={event => { setQuery(event.target.value); setPage(1); }} placeholder={my ? "Frontend၊ Python၊ DevOps ရှာရန်" : "Search frontend, Python, DevOps..."} className="w-full rounded-xl border border-line bg-surface px-11 py-3 text-sm" /></div><input aria-label="Technology" value={technology} onChange={event => { setTechnology(event.target.value); setPage(1); }} placeholder={my ? "Technology သို့မဟုတ် skill" : "Technology or skill"} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm" /><select aria-label="Career category" value={category} onChange={event => { setCategory(event.target.value); setPage(1); }} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">{my ? "Category အားလုံး" : "All categories"}</option>{categories.map(value => <option key={value} value={value}>{value}</option>)}</select><select aria-label="Learning level" value={level} onChange={event => { setLevel(event.target.value); setPage(1); }} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">{my ? "အဆင့်အားလုံး" : "All levels"}</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option><option value="professional">Professional</option></select><select aria-label="Duration" value={duration} onChange={event => { setDuration(event.target.value); setPage(1); }} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">{my ? "ကြာချိန်အားလုံး" : "Any duration"}</option><option value="short">Under 40 hours</option><option value="medium">40–120 hours</option><option value="long">Over 120 hours</option></select><select aria-label="Sort learning paths" value={sort} onChange={event => { setSort(event.target.value); setPage(1); }} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="title">{my ? "ခေါင်းစဉ်အလိုက်" : "Sort: title"}</option><option value="newest">{my ? "အသစ်ဆုံး" : "Sort: newest"}</option><option value="duration_asc">{my ? "ကြာချိန်တိုဆုံး" : "Sort: shortest"}</option><option value="duration_desc">{my ? "ကြာချိန်ရှည်ဆုံး" : "Sort: longest"}</option></select></div>
    <div className="mt-5 flex flex-wrap items-center justify-between gap-3"><p className="text-sm text-slate-400">{total} {my ? "လမ်းကြောင်း ရရှိနိုင်သည်" : "published learning paths"}</p>{hasFilters && <button className="text-sm text-indigo-300 hover:text-white" onClick={reset}>{my ? "စစ်ထုတ်မှုများ ဖျက်ရန်" : "Clear filters"}</button>}</div>
    {error ? <Card className="mt-8 border-red-400/20 bg-red-500/[.06] p-6 text-red-200" role="alert"><p>{my ? "လမ်းကြောင်းများကို မဖတ်နိုင်ပါ။" : "Unable to load learning paths."} {error}</p><button className="mt-4 rounded-lg border border-red-300/30 px-3 py-2 text-sm" onClick={() => setReload(value => value + 1)}>{my ? "ပြန်စစ်ရန်" : "Retry"}</button></Card> : loading ? <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{[1, 2, 3, 4, 5, 6].map(value => <Skeleton className="h-64" key={value} />)}</div> : <>
      {featured.length > 0 && !hasFilters && <section className="mt-8"><div className="mb-4"><p className="text-xs font-semibold uppercase tracking-[.18em] text-indigo-300">{my ? "အထူးရွေးချယ်ထားသော လမ်းကြောင်းများ" : "Featured learning paths"}</p><h2 className="mt-1 text-2xl font-bold">{my ? "စတင်ရန် အကောင်းဆုံးလမ်းကြောင်းများ" : "Start with a focused direction"}</h2></div><div className="grid gap-5 md:grid-cols-3">{featured.map(path => <PathCard key={path.id} path={path} enrollment={active.get(path.id)} my={my} featured />)}</div></section>}
      <section className="mt-10"><div className="mb-4"><p className="text-xs font-semibold uppercase tracking-[.18em] text-slate-500">{my ? "လမ်းကြောင်းအားလုံး" : "All learning paths"}</p></div><div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{allItems.map(path => <PathCard key={path.id} path={path} enrollment={active.get(path.id)} my={my} />)}{!items.length && <Card className="p-8 text-slate-400 md:col-span-3">{my ? "စစ်ထုတ်မှုနှင့် ကိုက်ညီသော published လမ်းကြောင်း မရှိသေးပါ။" : "No published learning paths matched these filters."}</Card>}</div>{pages > 1 && <nav aria-label="Learning path pagination" className="mt-8 flex flex-wrap items-center justify-center gap-4"><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:opacity-40" disabled={page === 1} onClick={() => setPage(value => value - 1)}>{my ? "ယခင်" : "Previous"}</button><span className="py-2 text-sm text-slate-400">{my ? `စာမျက်နှာ ${page} / ${pages}` : `Page ${page} of ${pages}`}</span><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:opacity-40" disabled={page === pages} onClick={() => setPage(value => value + 1)}>{my ? "နောက်" : "Next"}</button></nav>}</section>
    </>}
  </section>;
}

function PathCard({ path, enrollment, my, featured = false }: { path: Roadmap; enrollment?: LearningPathEnrollment; my: boolean; featured?: boolean }) {
  const progress = enrollment?.progress.progress_percent;
  return <Link href={`/learning-paths/${path.slug}`} className="group block h-full" aria-label={`${my ? "လမ်းကြောင်းဖွင့်ရန်" : "Open learning path"}: ${path.title}`}><Card className={`h-full p-6 transition hover:-translate-y-1 hover:border-indigo-400/50 ${featured ? "border-indigo-400/25 bg-gradient-to-br from-indigo-500/10 to-surface" : ""}`}><div className="flex items-center justify-between gap-3"><Badge>{path.career_category}</Badge>{enrollment && <span className="text-xs text-emerald-300">{my ? `${Math.round(progress ?? 0)}% လေ့လာနေသည်` : `${Math.round(progress ?? 0)}% in progress`}</span>}</div><BookOpen className="mt-6 text-indigo-300" size={24} /><h3 className="mt-4 text-xl font-bold">{path.title}</h3><p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-400">{path.description ?? path.description_en}</p><div className="mt-6 grid grid-cols-2 gap-2 text-xs text-slate-500"><span>{path.estimated_hours ? `${path.estimated_hours} ${my ? "နာရီ" : "hours"}` : (my ? "ကြာချိန် မသတ်မှတ်ရသေး" : "Duration pending")}</span><span>{path.stage_count ?? 0} {my ? "အဆင့်" : "stages"}</span><span>{path.course_count ?? 0} {my ? "သင်တန်း" : "courses"}</span><span>{path.project_count ?? 0} {my ? "ပရောဂျက်" : "projects"}</span></div><span className="mt-5 inline-flex items-center text-sm font-semibold text-indigo-300 group-hover:text-white">{enrollment ? (my ? "ဆက်လေ့လာရန်" : "Continue") : (my ? "လမ်းကြောင်းကြည့်ရန်" : "Explore")} <ArrowRight className="ml-1" size={14} /></span></Card></Link>;
}
