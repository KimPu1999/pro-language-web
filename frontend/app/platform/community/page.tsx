"use client";

import { useEffect, useState } from "react";
import { Card, Skeleton } from "@/components/ui";
import { csrf } from "@/components/auth-form";
import { communityApi } from "@/lib/ai-api";

export default function CommunityAdmin() {
  const [data, setData] = useState<any>();
  const [reports, setReports] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [categoryName, setCategoryName] = useState("");
  const [categorySlug, setCategorySlug] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const load = () => {
    setError("");
    Promise.all([communityApi.adminOverview(), communityApi.reports("open"), communityApi.adminCategories()]).then(([overview, reportPage, categoryRows]) => { setData(overview); setReports(reportPage.items ?? []); setCategories(categoryRows); }).catch(cause => setError(cause instanceof Error ? cause.message : "Unable to load moderation data."));
  };
  const createCategory = async () => { setBusy("category"); setError(""); try { await communityApi.adminCreateCategory({ name: categoryName, slug: categorySlug }, csrf()); setCategoryName(""); setCategorySlug(""); load(); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to create category."); } finally { setBusy(""); } };
  useEffect(load, []);
  const decide = async (id: string, status: string, action?: string) => {
    setBusy(id); setError("");
    try { await communityApi.decideReport(id, { status, action, note: action ? `Moderator action: ${action}` : "Reviewed by moderator." }, csrf()); load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to update report."); }
    finally { setBusy(""); }
  };
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><p className="text-sm text-indigo-300">Platform moderation</p><h1 className="mt-2 text-4xl font-bold">Community operations</h1><p className="mt-3 text-slate-400">Review reports and keep the learning space healthy. Every decision is authorized on the server and persisted in the moderation history.</p>{error && <Card className="mt-6 border-red-400/30 p-5 text-red-200" role="alert"><p>{error}</p><button className="mt-3 underline" onClick={load}>Retry</button></Card>}<div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{!data ? [1, 2, 3, 4].map(item => <Skeleton className="h-28" key={item} />) : [["Posts", data.posts], ["Comments", data.comments], ["Open reports", data.open_reports], ["Groups", data.groups]].map(([label, value]) => <Card key={String(label)} className="p-5"><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-3xl font-bold">{value}</p></Card>)}</div><Card className="mt-8 p-5"><h2 className="font-semibold">Community categories</h2><div className="mt-4 flex flex-wrap gap-2">{categories.map(category => <span className="rounded-full bg-elevated px-3 py-1 text-xs text-slate-300" key={category.id}>{category.name}</span>)}{!categories.length && <span className="text-sm text-slate-500">No categories have been created yet.</span>}</div><div className="mt-5 grid gap-3 sm:grid-cols-[1fr_1fr_auto]"><input value={categoryName} onChange={event => setCategoryName(event.target.value)} placeholder="Category name" className="rounded-lg bg-ink px-3 py-2 text-sm"/><input value={categorySlug} onChange={event => setCategorySlug(event.target.value)} placeholder="category-slug" className="rounded-lg bg-ink px-3 py-2 text-sm"/><button disabled={busy === "category" || !categoryName.trim() || !categorySlug.trim()} onClick={createCategory} className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold disabled:opacity-50">Add category</button></div></Card><Card className="mt-8 overflow-hidden"><div className="border-b border-line p-5"><h2 className="font-semibold">Reports queue</h2><p className="mt-1 text-sm text-slate-500">Reporter identity is intentionally hidden from this queue.</p></div>{reports.length ? reports.map(report => <div key={report.id} className="flex flex-col gap-4 border-b border-line/60 p-5 text-sm lg:flex-row lg:items-center lg:justify-between"><div><p className="font-medium">{report.target_type} · {report.reason}</p><p className="mt-1 text-slate-500">{report.status} · {new Date(report.created_at).toLocaleString()}</p></div><div className="flex flex-wrap gap-2"><button disabled={busy === report.id} onClick={() => decide(report.id, "under_review")} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300 disabled:opacity-50">Review</button><button disabled={busy === report.id} onClick={() => decide(report.id, "resolved", "hide")} className="rounded-lg bg-amber-500/15 px-3 py-2 text-xs text-amber-200 disabled:opacity-50">Hide</button><button disabled={busy === report.id} onClick={() => decide(report.id, "resolved")} className="rounded-lg bg-emerald-500/15 px-3 py-2 text-xs text-emerald-200 disabled:opacity-50">Resolve</button><button disabled={busy === report.id} onClick={() => decide(report.id, "dismissed")} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-400 disabled:opacity-50">Dismiss</button></div></div>) : <p className="p-6 text-slate-400">No open reports.</p>}</Card></section>;
}
