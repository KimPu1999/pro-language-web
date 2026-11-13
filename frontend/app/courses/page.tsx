"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { api } from "@/lib/api";
import type { Course, Language } from "@/lib/types";
import { Badge, Card, Skeleton } from "@/components/ui";

type Category = { id: string; name: string; slug: string };

export default function Courses() {
  const [items, setItems] = useState<Course[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [level, setLevel] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.allSettled([api.languages(), api.categories()]).then(([languageResult, categoryResult]) => {
      if (languageResult.status === "fulfilled") setLanguages(languageResult.value);
      if (categoryResult.status === "fulfilled") setCategories(categoryResult.value);
    });
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      const params = new URLSearchParams();
      if (query) params.set("search", query);
      if (language) params.set("language", language);
      if (level) params.set("level", level);
      if (category) params.set("category", category);
      params.set("page", String(page));
      params.set("page_size", "12");
      setLoading(true); setError("");
      api.courses(`?${params}`).then(result => { setItems(result.items); setPages(result.pages); setTotal(result.total); }).catch(e => setError(e instanceof Error ? e.message : "Unable to load courses")).finally(() => setLoading(false));
    }, 200);
    return () => clearTimeout(timer);
  }, [query, language, level, category, page]);

  const activeFilters = useMemo(() => [language, level, category].filter(Boolean).length, [language, level, category]);
  return <section className="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <div><p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-300">Free course catalog</p><h1 className="mt-2 text-4xl font-bold tracking-tight">Learn programming from first principles</h1><p className="mt-4 max-w-3xl text-slate-400">Choose a language, follow its prerequisites, and learn the theory before you ever need to write or execute code.</p></div>
    <div className="mt-8 grid gap-3 lg:grid-cols-[minmax(0,1fr)_180px_180px_180px]"><div className="relative"><Search className="absolute left-4 top-3.5 text-slate-500" size={19}/><input aria-label="Search courses" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search Python, C, SQL..." className="w-full rounded-xl border border-line bg-surface px-11 py-3 text-sm text-white placeholder:text-slate-500"/></div><select aria-label="Programming language" value={language} onChange={e => setLanguage(e.target.value)} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">All languages</option>{languages.map(item => <option key={item.id} value={item.slug}>{item.name}</option>)}</select><select aria-label="Course level" value={level} onChange={e => setLevel(e.target.value)} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">All levels</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option><option value="professional">Professional</option></select><select aria-label="Course category" value={category} onChange={e => setCategory(e.target.value)} className="rounded-xl border border-line bg-surface px-4 py-3 text-sm"><option value="">All categories</option>{categories.map(item => <option key={item.id} value={item.slug}>{item.name}</option>)}</select></div>
    <div className="mt-5 flex items-center justify-between text-sm text-slate-500"><span>{activeFilters ? `${activeFilters} filters active · ${total} courses` : `${total || "Published"} courses`}</span>{(query || activeFilters > 0) && <button className="text-indigo-300 hover:text-white" onClick={() => { setQuery(""); setLanguage(""); setLevel(""); setCategory(""); setPage(1); }}>Clear filters</button>}</div>
    {error ? <div className="mt-8 rounded-2xl border border-red-400/30 bg-red-500/10 p-6 text-red-300" role="alert">Unable to load courses. {error}</div> : loading ? <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map(i => <Skeleton className="h-64" key={i}/>)}</div> : <><div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{items.map(course => <Link key={course.id} href={`/courses/${course.slug}`}><Card className="h-full p-5 transition hover:-translate-y-1 hover:border-indigo-400/50"><div className="flex justify-between"><Badge>{course.language.name}</Badge><span className="text-xs text-slate-500">Free · {course.level}</span></div><h2 className="mt-5 text-xl font-bold">{course.title}</h2><p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-400">{course.description}</p><div className="mt-6 flex justify-between text-xs text-slate-500"><span>{course.category.name}</span><span>{Math.max(1, Math.round(course.duration_minutes / 60))} hours</span></div></Card></Link>)}{!items.length && <Card className="p-8 text-slate-400 md:col-span-2 lg:col-span-3">No published courses matched these filters.</Card>}</div>{pages > 1 && <nav aria-label="Course pagination" className="mt-8 flex items-center justify-center gap-4"><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40" disabled={page <= 1} onClick={() => setPage(value => value - 1)}>Previous</button><span className="text-sm text-slate-400">Page {page} of {pages}</span><button className="rounded-lg border border-line px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40" disabled={page >= pages} onClick={() => setPage(value => value + 1)}>Next</button></nav>}</>}
  </section>;
}
