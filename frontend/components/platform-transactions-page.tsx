"use client";

import { useCallback, useEffect, useState } from "react";
import { transactionsApi } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Card, EmptyState, Skeleton } from "@/components/ui";

type TransactionState = {
  configured: boolean;
  status: string;
  data_source: string;
  message: string;
  items: unknown[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
};

export function PlatformTransactionsPage() {
  const { locale } = useI18n();
  const my = locale === "my";
  const [data, setData] = useState<TransactionState | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const copy = my ? {
    eyebrow: "ငွေပေးချေမှု စီမံခန့်ခွဲမှု", title: "Transactions", description: "ငွေပေးချေမှု provider မချိတ်ဆက်ရသေးသောကြောင့် transaction record များ မရရှိနိုင်သေးပါ။", refresh: "ပြန်စစ်ရန်", search: "Transaction ID သို့မဟုတ် ကျောင်းသားရှာရန်", all: "အခြေအနေအားလုံး", empty: "Transaction မရှိသေးပါ", unavailable: "ဤ deployment တွင် billing provider မသတ်မှတ်ရသေးပါ။ ငွေကြေးမှတ်တမ်းအတုများကို မပြပါ။", source: "ဒေတာရင်းမြစ်"
  } : {
    eyebrow: "Financial operations", title: "Transactions", description: "Payment provider configuration is required before transaction records can be displayed.", refresh: "Retry", search: "Search transaction ID or student", all: "All statuses", empty: "No transactions", unavailable: "Billing is not configured for this deployment. No synthetic financial records are displayed.", source: "Data source"
  };
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const params = new URLSearchParams({ page: "1", page_size: "25" });
      if (search.trim()) params.set("search", search.trim());
      if (status) params.set("status", status);
      setData(await transactionsApi.list(`?${params.toString()}`));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Transactions API unavailable"); }
    finally { setLoading(false); }
  }, [search, status]);
  useEffect(() => { void load(); }, [load]);
  return <section className="space-y-7">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-indigo-300">{copy.eyebrow}</p><h1 className="mt-2 text-3xl font-bold">{copy.title}</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{copy.description}</p></div><button onClick={() => void load()} disabled={loading} className="rounded-xl border border-line px-4 py-2.5 text-sm font-semibold hover:bg-elevated">{copy.refresh}</button></div>
    {error && <Card className="p-5" role="alert"><p className="text-sm text-red-300">{error}</p><button onClick={() => void load()} className="mt-4 rounded-lg bg-primary px-3 py-2 text-sm font-semibold">{copy.refresh}</button></Card>}
    <Card className="flex flex-wrap gap-3 p-4"><input value={search} onChange={event => setSearch(event.target.value)} placeholder={copy.search} className="min-w-[240px] flex-1 rounded-xl border border-line bg-ink px-3 py-2.5 text-sm"/><select value={status} onChange={event => setStatus(event.target.value)} className="rounded-xl border border-line bg-ink px-3 py-2.5 text-sm"><option value="">{copy.all}</option><option value="paid">Paid</option><option value="pending">Pending</option><option value="refunded">Refunded</option><option value="failed">Failed</option></select></Card>
    {loading ? <Skeleton className="h-64"/> : data?.configured ? <Card className="overflow-x-auto p-5"><table className="w-full min-w-[720px] text-left text-sm"><thead><tr className="border-b border-line text-slate-500"><th className="px-3 py-3">ID</th><th className="px-3 py-3">Student</th><th className="px-3 py-3">Amount</th><th className="px-3 py-3">Status</th><th className="px-3 py-3">Created</th></tr></thead><tbody>{data.items.map((item: any) => <tr key={item.id} className="border-b border-line/60"><td className="px-3 py-3">{item.id}</td><td className="px-3 py-3">{item.student_name}</td><td className="px-3 py-3">{item.amount} {item.currency}</td><td className="px-3 py-3">{item.status}</td><td className="px-3 py-3">{item.created_at}</td></tr>)}</tbody></table></Card> : <Card className="p-8"><div className="mb-5 rounded-xl border border-amber-400/20 bg-amber-400/5 p-4"><p className="text-sm font-semibold text-amber-200">{copy.unavailable}</p><p className="mt-2 text-xs text-slate-400">{copy.source}: {data?.data_source ?? "unknown"}</p></div><EmptyState title={copy.empty} description={data?.message ?? copy.unavailable}/></Card>}
  </section>;
}
