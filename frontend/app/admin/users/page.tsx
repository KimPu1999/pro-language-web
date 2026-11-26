"use client";

import { useCallback, useEffect, useState } from "react";
import { Search, ShieldCheck, Users } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, Skeleton } from "@/components/ui";

type UserRow = { id: string; email: string; display_name: string; role: string; account_status: string; email_verified: boolean; created_at: string };
type UserPage = { items: UserRow[]; page: number; page_size: number; total: number; pages: number };

function roleLabel(value: string) { return value.replaceAll("_", " "); }

export default function AdminUsersPage() {
  const [data, setData] = useState<UserPage | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const query = new URLSearchParams({ page: String(page), page_size: "20" });
    if (search.trim()) query.set("search", search.trim());
    api.adminUsers(`?${query.toString()}`).then(setData).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load users")).finally(() => setLoading(false));
  }, [page, search]);

  useEffect(() => { load(); }, [load]);

  return <div>
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-300">Governance</p><h1 className="mt-2 text-3xl font-bold tracking-tight">Admin users</h1><p className="mt-2 text-sm text-slate-400">Review management accounts and access state from the live database.</p></div>
      <div className="flex items-center gap-2 text-xs text-slate-500"><ShieldCheck size={15} className="text-indigo-300" /> Role access is enforced by the API</div>
    </div>
    <Card className="mt-7 p-4 sm:p-5">
      <label className="flex max-w-xl items-center gap-3 rounded-xl border border-line bg-surface px-3.5 py-2.5 text-sm text-slate-500 focus-within:border-indigo-400/50"><Search size={16} /><input aria-label="Search admin users" value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} placeholder="Search name, email, or role…" className="w-full bg-transparent text-slate-200 outline-none placeholder:text-slate-600" /></label>
      {error && <div role="alert" className="mt-4 rounded-xl border border-rose-400/20 bg-rose-400/10 p-4 text-sm text-rose-200">{error}<Button onClick={load} className="ml-4">Retry</Button></div>}
      {loading ? <div className="mt-5 space-y-3">{Array.from({ length: 5 }, (_, index) => <Skeleton key={index} className="h-14" />)}</div> : <div className="mt-5 overflow-x-auto rounded-xl border border-line"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-surface text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-4 py-3">User</th><th className="px-4 py-3">Role</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Email</th><th className="px-4 py-3">Created</th></tr></thead><tbody>{data?.items.length ? data.items.map((user) => <tr key={user.id} className="border-t border-line"><td className="px-4 py-4"><p className="font-medium text-slate-100">{user.display_name}</p><p className="mt-1 text-xs text-slate-500">{user.email}</p></td><td className="px-4 py-4 capitalize text-slate-300">{roleLabel(user.role)}</td><td className="px-4 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${user.account_status === "active" ? "bg-emerald-400/10 text-emerald-200" : "bg-amber-400/10 text-amber-200"}`}>{user.account_status}</span></td><td className="px-4 py-4 text-slate-400">{user.email_verified ? "Verified" : "Unverified"}</td><td className="px-4 py-4 text-slate-500">{new Date(user.created_at).toLocaleDateString()}</td></tr>) : <tr><td colSpan={5} className="px-4 py-12 text-center text-sm text-slate-500"><Users className="mx-auto mb-3 opacity-50" size={24} />No users match this search.</td></tr>}</tbody></table></div>}
      <div className="mt-4 flex items-center justify-between gap-3 text-xs text-slate-500"><span>{data?.total ?? 0} users</span><div className="flex items-center gap-2"><button disabled={page <= 1 || loading} onClick={() => setPage((value) => Math.max(1, value - 1))} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Previous</button><span>{data?.page ?? page} / {Math.max(data?.pages ?? 0, 1)}</span><button disabled={loading || page >= (data?.pages ?? 0)} onClick={() => setPage((value) => value + 1)} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Next</button></div></div>
    </Card>
  </div>;
}
