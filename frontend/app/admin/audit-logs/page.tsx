"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Search } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, Skeleton } from "@/components/ui";

type AuditRow = { id: string; action: string; entity_type: string; entity_id: string | null; actor_id: string | null; created_at: string };
type AuditPage = { items: AuditRow[]; page: number; page_size: number; total: number; pages: number };

function label(value: string) { return value.replaceAll("_", " "); }

export default function AdminAuditLogsPage() {
  const [data, setData] = useState<AuditPage | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const query = new URLSearchParams({ page: String(page), page_size: "20" });
    if (search.trim()) query.set("search", search.trim());
    api.adminAuditLogs(`?${query.toString()}`).then(setData).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load audit logs")).finally(() => setLoading(false));
  }, [page, search]);

  useEffect(() => { load(); }, [load]);

  return <div>
    <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-300">Governance</p><h1 className="mt-2 text-3xl font-bold tracking-tight">Audit logs</h1><p className="mt-2 text-sm text-slate-400">Inspect recorded administrative actions and their entities.</p></div><div className="flex items-center gap-2 text-xs text-slate-500"><Activity size={15} className="text-indigo-300" /> Live database records</div></div>
    <Card className="mt-7 p-4 sm:p-5">
      <label className="flex max-w-xl items-center gap-3 rounded-xl border border-line bg-surface px-3.5 py-2.5 text-sm text-slate-500 focus-within:border-indigo-400/50"><Search size={16} /><input aria-label="Search audit logs" value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} placeholder="Search action or entity type…" className="w-full bg-transparent text-slate-200 outline-none placeholder:text-slate-600" /></label>
      {error && <div role="alert" className="mt-4 rounded-xl border border-rose-400/20 bg-rose-400/10 p-4 text-sm text-rose-200">{error}<Button onClick={load} className="ml-4">Retry</Button></div>}
      {loading ? <div className="mt-5 space-y-3">{Array.from({ length: 6 }, (_, index) => <Skeleton key={index} className="h-14" />)}</div> : <div className="mt-5 overflow-x-auto rounded-xl border border-line"><table className="w-full min-w-[800px] text-left text-sm"><thead className="bg-surface text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-4 py-3">Action</th><th className="px-4 py-3">Entity</th><th className="px-4 py-3">Actor</th><th className="px-4 py-3">Recorded</th></tr></thead><tbody>{data?.items.length ? data.items.map((item) => <tr key={item.id} className="border-t border-line"><td className="px-4 py-4 font-medium capitalize text-slate-100">{label(item.action)}</td><td className="px-4 py-4"><p className="capitalize text-slate-300">{label(item.entity_type)}</p><p className="mt-1 text-xs text-slate-500">{item.entity_id ?? "No entity id"}</p></td><td className="px-4 py-4 text-xs text-slate-400">{item.actor_id ?? "System"}</td><td className="px-4 py-4 text-slate-500">{new Date(item.created_at).toLocaleString()}</td></tr>) : <tr><td colSpan={4} className="px-4 py-12 text-center text-sm text-slate-500"><Activity className="mx-auto mb-3 opacity-50" size={24} />No audit events match this search.</td></tr>}</tbody></table></div>}
      <div className="mt-4 flex items-center justify-between gap-3 text-xs text-slate-500"><span>{data?.total ?? 0} audit events</span><div className="flex items-center gap-2"><button disabled={page <= 1 || loading} onClick={() => setPage((value) => Math.max(1, value - 1))} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Previous</button><span>{data?.page ?? page} / {Math.max(data?.pages ?? 0, 1)}</span><button disabled={loading || page >= (data?.pages ?? 0)} onClick={() => setPage((value) => value + 1)} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Next</button></div></div>
    </Card>
  </div>;
}
