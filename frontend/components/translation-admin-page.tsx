"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowUpRight as ExternalLink, Check as CheckCircle2, CircleAlert as AlertTriangle, Languages, Search } from "lucide-react";
import { translationApi } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Badge, Card, Skeleton } from "@/components/ui";

type Item = { source_type: string; source_id: string; course_id?: string; title: string; status: string; published: boolean; has_burmese: boolean; translation_state: "available" | "missing" | "partial"; edit_url: string };

export function TranslationAdminPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<Item[]>([]);
  const [summary, setSummary] = useState<{ total: number; available: number; missing: number; published_total: number; published_missing: number; data_source: string } | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");
  useEffect(() => { translationApi.coverage().then(result => { setItems(result.items); setSummary(result.summary); }).catch(reason => setError(reason instanceof Error ? reason.message : "Unable to load translation coverage")); }, []);
  const visible = useMemo(() => items.filter(item => (filter === "all" || item.translation_state === filter) && item.title.toLowerCase().includes(query.toLowerCase())), [filter, items, query]);
  if (error) return <Card className="p-6"><p className="text-sm text-red-300">{error}</p></Card>;
  if (!summary) return <div className="space-y-5"><Skeleton className="h-12"/><Skeleton className="h-96"/></div>;
  return <div className="space-y-6">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><div className="flex items-center gap-2 text-sm font-semibold text-indigo-300"><Languages size={16}/> {t("platformControl")}</div><h1 className="mt-2 text-3xl font-bold">{t("translations")}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{t("translationCoverage")}. This report reads the database and keeps unpublished Burmese content out of the public experience.</p></div><Badge className="border border-line bg-surface text-slate-300">{summary.data_source}</Badge></div>
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><Card className="p-5"><p className="text-xs text-slate-500">Total items</p><p className="mt-2 text-2xl font-bold">{summary.total}</p></Card><Card className="p-5"><p className="text-xs text-slate-500">{t("available")}</p><p className="mt-2 text-2xl font-bold text-emerald-300">{summary.available}</p></Card><Card className="p-5"><p className="text-xs text-slate-500">{t("missing")}</p><p className="mt-2 text-2xl font-bold text-amber-200">{summary.missing}</p></Card><Card className="p-5"><p className="text-xs text-slate-500">Published missing</p><p className="mt-2 text-2xl font-bold text-red-300">{summary.published_missing}</p></Card></div>
    <Card className="overflow-hidden"><div className="flex flex-wrap gap-3 border-b border-line p-4"><label className="flex min-w-[220px] flex-1 items-center gap-2 rounded-lg border border-line bg-ink px-3 py-2 text-sm text-slate-400"><Search size={16}/><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search translation items" className="w-full bg-transparent outline-none"/></label><select value={filter} onChange={event => setFilter(event.target.value)} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm text-slate-300"><option value="all">All statuses</option><option value="missing">{t("missing")}</option><option value="partial">Partial</option><option value="available">{t("available")}</option></select></div><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="border-b border-line bg-surface/60 text-xs uppercase tracking-[0.12em] text-slate-500"><tr><th className="px-4 py-3">Content</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">Publication</th><th className="px-4 py-3">Myanmar</th><th className="px-4 py-3">Action</th></tr></thead><tbody className="divide-y divide-line/70">{visible.map(item => <tr key={`${item.source_type}-${item.source_id}`}><td className="px-4 py-3"><p className="font-medium text-slate-200">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.status}</p></td><td className="px-4 py-3 capitalize text-slate-400">{item.source_type.replaceAll("_", " ")}</td><td className="px-4 py-3">{item.published ? <Badge className="bg-emerald-400/10 text-emerald-300">Published</Badge> : <Badge className="bg-surface text-slate-400">Draft</Badge>}</td><td className="px-4 py-3">{item.translation_state === "available" ? <span className="inline-flex items-center gap-1 text-emerald-300"><CheckCircle2 size={15}/> {t("available")}</span> : <span className="inline-flex items-center gap-1 text-amber-200"><AlertTriangle size={15}/> {item.translation_state === "partial" ? "Partial" : t("missing")}</span>}</td><td className="px-4 py-3"><Link href={item.edit_url} className="inline-flex items-center gap-1 text-indigo-300 hover:text-indigo-200">{item.source_type === "lesson" ? t("editCurriculum") : t("reviewQueue")} <ExternalLink size={14}/></Link></td></tr>)}</tbody></table>{visible.length === 0 && <p className="p-8 text-center text-sm text-slate-500">No translation items match this filter.</p>}</div></Card>
  </div>;
}
