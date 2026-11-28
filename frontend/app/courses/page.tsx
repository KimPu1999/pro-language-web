"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { api, coursesApi } from "@/lib/api";
import type { Course, Language } from "@/lib/types";
import { Badge, Card, Skeleton } from "@/components/ui";
import { useI18n } from "@/lib/i18n";

type Category = { id: string; name: string; slug: string };
type SortOrder = "title_asc" | "title_desc" | "newest" | "duration_asc" | "duration_desc";
type Filters = { search: string; language: string; difficulty: string; category: string; sort: SortOrder; page: number };

const PAGE_SIZE = 10;
const DEFAULT_SORT: SortOrder = "title_asc";
const SORT_VALUES: SortOrder[] = ["title_asc", "title_desc", "newest", "duration_asc", "duration_desc"];

function readFilters(params: URLSearchParams): Filters {
  const parsedPage = Number.parseInt(params.get("page") ?? "1", 10);
  const requestedSort = params.get("sort") as SortOrder | null;
  return { search: params.get("search") ?? "", language: params.get("language") ?? "", difficulty: params.get("difficulty") ?? params.get("level") ?? "", category: params.get("category") ?? "", sort: requestedSort && SORT_VALUES.includes(requestedSort) ? requestedSort : DEFAULT_SORT, page: Number.isFinite(parsedPage) && parsedPage > 0 ? parsedPage : 1 };
}

function toQuery(filters: Filters) {
  const params = new URLSearchParams();
  if (filters.search.trim()) params.set("search", filters.search.trim());
  if (filters.language) params.set("language", filters.language);
  if (filters.difficulty) params.set("difficulty", filters.difficulty);
  if (filters.category) params.set("category", filters.category);
  if (filters.sort !== DEFAULT_SORT) params.set("sort", filters.sort);
  if (filters.page > 1) params.set("page", String(filters.page));
  params.set("page_size", String(PAGE_SIZE));
  return params.toString();
}

export default function Courses() {
  const { t } = useI18n();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const urlKey = searchParams.toString();
  const [filters, setFilters] = useState<Filters>(() => readFilters(new URLSearchParams(urlKey)));
  const [items, setItems] = useState<Course[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [pages, setPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { setFilters(readFilters(new URLSearchParams(urlKey))); }, [urlKey]);

  useEffect(() => {
    Promise.allSettled([api.languages(), api.categories()]).then(([languageResult, categoryResult]) => {
      if (languageResult.status === "fulfilled") setLanguages(languageResult.value);
      if (categoryResult.status === "fulfilled") setCategories(categoryResult.value);
    });
  }, []);

  useEffect(() => {
    let current = true;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setLoading(true); setError("");
      coursesApi(`?${toQuery(filters)}`, controller.signal).then(result => {
        if (!current) return;
        setItems(result.items); setPages(result.pages); setTotal(result.total);
      }).catch(reason => {
        if (current && !controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Unable to load courses");
      }).finally(() => { if (current) setLoading(false); });
    }, 200);
    return () => { current = false; clearTimeout(timer); controller.abort(); };
  }, [filters]);

  const updateFilters = (patch: Partial<Filters>, resetPage = true) => {
    const next = { ...filters, ...patch, page: resetPage ? 1 : patch.page ?? filters.page };
    const query = toQuery(next);
    router.push(`${pathname}${query ? `?${query}` : ""}`);
  };

  const activeFilters = useMemo(() => [
    filters.search ? `Search: ${filters.search}` : "",
    filters.language ? `Language: ${languages.find(item => item.slug === filters.language)?.name ?? filters.language}` : "",
    filters.difficulty ? `Difficulty: ${filters.difficulty}` : "",
    filters.category ? `Category: ${categories.find(item => item.slug === filters.category)?.name ?? filters.category}` : "",
    filters.sort !== DEFAULT_SORT ? `Sort: ${filters.sort.replaceAll("_", " ")}` : "",
  ].filter(Boolean), [categories, filters, languages]);

  return <section className="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <div><p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-300">{t("courses")}</p><h1 className="mt-2 text-4xl font-bold tracking-tight">{t("learnProgramming")}</h1><p className="mt-4 max-w-3xl text-slate-400">{t("chooseLanguage")}</p></div>
    <div className="mt-6 grid gap-2.5 md:grid-cols-2 lg:grid-cols-[minmax(0,1fr)_150px_150px_150px_165px]">
      <div className="relative"><Search className="absolute left-3.5 top-3 text-slate-500" size={17}/><input aria-label={`${t("search")} ${t("courses")}`} value={filters.search} onChange={event => updateFilters({ search: event.target.value })} placeholder="Search Python, C, SQL..." className="h-10 w-full rounded-lg border border-line bg-surface px-10 text-sm text-white placeholder:text-slate-500"/></div>
      <select aria-label={t("language")} value={filters.language} onChange={event => updateFilters({ language: event.target.value })} className="h-10 min-w-0 rounded-lg border border-line bg-surface px-3 text-sm"><option value="">All languages</option>{languages.map(item => <option key={item.id} value={item.slug}>{item.name}</option>)}</select>
      <select aria-label="Course difficulty" value={filters.difficulty} onChange={event => updateFilters({ difficulty: event.target.value })} className="h-10 min-w-0 rounded-lg border border-line bg-surface px-3 text-sm"><option value="">All difficulties</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option><option value="professional">Professional</option></select>
      <select aria-label="Course category" value={filters.category} onChange={event => updateFilters({ category: event.target.value })} className="h-10 min-w-0 rounded-lg border border-line bg-surface px-3 text-sm"><option value="">All categories</option>{categories.map(item => <option key={item.id} value={item.slug}>{item.name}</option>)}</select>
      <select aria-label="Sort courses" value={filters.sort} onChange={event => updateFilters({ sort: event.target.value as SortOrder })} className="h-10 min-w-0 rounded-lg border border-line bg-surface px-3 text-sm"><option value="title_asc">Title A–Z</option><option value="title_desc">Title Z–A</option><option value="newest">Newest</option><option value="duration_asc">Shortest first</option><option value="duration_desc">Longest first</option></select>
    </div>
    <div className="mt-5 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-500"><span>{activeFilters.length ? `${activeFilters.length} filters active · ${total} courses` : `${total || "Published"} courses`}</span><div className="flex flex-wrap items-center gap-2">{activeFilters.map(filter => <Badge key={filter}>{filter}</Badge>)}{activeFilters.length > 0 && <button className="text-indigo-300 hover:text-white" onClick={() => updateFilters({ search: "", language: "", difficulty: "", category: "", sort: DEFAULT_SORT })}>Clear filters</button>}</div></div>
    {error ? <div className="mt-8 rounded-2xl border border-red-400/30 bg-red-500/10 p-6 text-red-300" role="alert">Unable to load courses. {error}</div> : loading ? <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map(i => <Skeleton className="h-64" key={i}/>)}</div> : <><div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{items.map(course => <Link key={course.id} href={`/courses/${course.slug}`}><Card className="h-full overflow-hidden p-0 transition hover:-translate-y-1 hover:border-indigo-400/50"><div className="flex h-36 items-center justify-center border-b border-line bg-gradient-to-br from-indigo-500/10 to-violet-500/5 p-5">{course.card_logo_url ? <img src={course.card_logo_url} alt={course.card_image_alt || `${course.display_title || course.title} logo`} className="h-24 w-full object-contain" loading="lazy" /> : <div className="grid h-20 w-20 place-items-center rounded-2xl bg-indigo-500/15 text-2xl font-bold text-indigo-200">{(course.display_title || course.title).slice(0, 1)}</div>}</div><div className="flex h-[260px] flex-col p-5"><div className="flex items-start justify-between gap-3"><div><Badge>{course.technology_name || course.language.name}</Badge><h2 className="mt-3 line-clamp-2 text-xl font-bold">{course.display_title || course.title}</h2></div><span className="shrink-0 text-xs text-slate-500">Free</span></div><p className="mt-3 line-clamp-2 text-sm leading-6 text-slate-400">{course.card_short_description || course.short_description || course.description}</p><div className="mt-auto"><div className="flex items-center gap-2 text-xs text-slate-500">{course.show_rating !== false ? course.rating_count ? <><span className="flex items-center gap-1 text-amber-300"><span aria-hidden="true">★</span> {course.rating_average?.toFixed(1)}</span><span>({course.rating_count} reviews)</span></> : <span>No ratings yet</span> : null}<span className="ml-auto">{course.level}</span></div><div className="mt-4 flex items-center justify-between border-t border-line pt-3 text-xs text-slate-500"><span>{course.category.name}</span><span className="text-emerald-300">Available</span></div><p className="mt-2 text-xs text-slate-500">{course.duration_minutes ? `${Math.round(course.duration_minutes / 60)} hours estimated` : "Editorial estimate pending"}</p></div></div></Card></Link>)}{!items.length && <Card className="p-8 text-slate-400 md:col-span-2 lg:col-span-3">No published courses matched these filters.</Card>}</div>{pages > 1 && <nav aria-label="Course pagination" className="mt-8 flex items-center justify-center gap-4"><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40" disabled={filters.page <= 1} onClick={() => updateFilters({ page: filters.page - 1 }, false)}>Previous</button><span className="text-sm text-slate-400">Page {filters.page} of {pages}</span><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40" disabled={filters.page >= pages} onClick={() => updateFilters({ page: filters.page + 1 }, false)}>Next</button></nav>}</>}
  </section>;
}
