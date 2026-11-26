"use client";

import Link from "next/link";
import { ArrowUpRight, BookOpen, Plus, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { AdminCourse } from "@/lib/types";
import { Badge, Button, Card, Skeleton } from "@/components/ui";

export default function AdminCourses() {
  const [items, setItems] = useState<AdminCourse[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => { api.adminCourses().then(r => setItems(r.items)).catch(e => setError(e.message)); }, []);

  const filteredItems = useMemo(() => items.filter(item => {
    const value = query.trim().toLowerCase();
    return !value || item.title.toLowerCase().includes(value) || item.slug.toLowerCase().includes(value);
  }), [items, query]);

  return <section>
    <div className="flex flex-wrap items-end justify-between gap-5">
      <div><div className="flex items-center gap-2 text-sm font-semibold text-indigo-300"><BookOpen size={16}/> Content library</div><h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">Courses</h1><p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">Create, organize, and publish the learning experiences available on your platform.</p></div>
      <Link href="/admin/courses/new"><Button className="inline-flex items-center gap-2 shadow-lg shadow-indigo-500/20"><Plus size={17}/>Create course</Button></Link>
    </div>

    {error && <Card className="mt-7 border-red-400/20 bg-red-500/5 p-5 text-sm text-red-300">{error}</Card>}
    {!items.length && !error ? <Skeleton className="mt-8 h-64"/> : <>
      <div className="mt-8 grid gap-3 sm:grid-cols-3"><Card className="p-4"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Total courses</p><p className="mt-2 text-2xl font-bold">{items.length}</p></Card><Card className="p-4"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Published</p><p className="mt-2 text-2xl font-bold text-emerald-300">{items.filter(item => item.status === "published").length}</p></Card><Card className="p-4"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Drafts & archived</p><p className="mt-2 text-2xl font-bold text-amber-200">{items.filter(item => item.status !== "published").length}</p></Card></div>
      <Card className="mt-6 overflow-hidden border-line/80 shadow-2xl shadow-slate-950/20">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line/80 bg-surface/70 px-5 py-4 sm:px-6"><div><h2 className="font-semibold">Course catalog</h2><p className="mt-1 text-xs text-slate-500">{filteredItems.length} of {items.length} courses</p></div><label className="flex h-10 w-full max-w-xs items-center gap-2 rounded-lg border border-line bg-ink/40 px-3 text-sm text-slate-500 focus-within:border-indigo-400/60"><Search size={15}/><input aria-label="Search courses" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search courses…" className="w-full bg-transparent text-slate-200 outline-none placeholder:text-slate-600"/></label></div>
        <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="border-b border-line/80 bg-elevated/40 text-xs uppercase tracking-[0.12em] text-slate-500"><tr><th className="px-5 py-4 font-semibold sm:px-6">Course</th><th className="px-5 py-4 font-semibold">Level</th><th className="px-5 py-4 font-semibold">Status</th><th className="px-5 py-4 text-right font-semibold sm:px-6">Action</th></tr></thead><tbody className="divide-y divide-line/70">{filteredItems.map(course => <tr key={course.id} className="group transition hover:bg-indigo-400/[0.035]"><td className="px-5 py-4 sm:px-6"><p className="max-w-[680px] font-semibold leading-5 text-slate-100">{course.title}</p><p className="mt-1 font-mono text-[11px] text-slate-500">{course.slug}</p></td><td className="px-5 py-4 capitalize text-slate-400">{course.level}</td><td className="px-5 py-4"><Badge className={course.status === "published" ? "bg-emerald-400/10 text-emerald-300" : "bg-amber-400/10 text-amber-200"}>{course.status}</Badge></td><td className="px-5 py-4 text-right sm:px-6"><Link className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 font-medium text-indigo-300 transition hover:bg-indigo-400/10 hover:text-indigo-200" href={`/admin/courses/${course.id}/builder`}>Open builder<ArrowUpRight size={15}/></Link></td></tr>)}</tbody></table></div>
        {!filteredItems.length && <p className="px-6 py-12 text-center text-sm text-slate-500">No courses match “{query}”.</p>}
      </Card>
    </>}
  </section>;
}
