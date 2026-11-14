"use client";

import { useMemo, useState } from "react";

type Row = { orderId: number; region: string; channel: string; revenue: number; orders: number };

const SAMPLE: Row[] = [
  { orderId: 1001, region: "North", channel: "Online", revenue: 1200, orders: 12 },
  { orderId: 1002, region: "South", channel: "Retail", revenue: 900, orders: 9 },
  { orderId: 1003, region: "North", channel: "Retail", revenue: 500, orders: 5 },
  { orderId: 1004, region: "East", channel: "Online", revenue: 1500, orders: 15 },
  { orderId: 1005, region: "South", channel: "Online", revenue: 1100, orders: 11 },
  { orderId: 1006, region: "West", channel: "Retail", revenue: 700, orders: 7 },
  { orderId: 1007, region: "East", channel: "Retail", revenue: 800, orders: 8 },
  { orderId: 1008, region: "West", channel: "Online", revenue: 1300, orders: 13 },
];

export function DataAnalysisLab({ title }: { title: string }) {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("all");
  const [sort, setSort] = useState<"orderId" | "revenue">("orderId");
  const [page, setPage] = useState(1);
  const pageSize = 5;

  const filtered = useMemo(() => SAMPLE.filter((row) => {
    const matchesText = `${row.orderId} ${row.region} ${row.channel}`.toLowerCase().includes(query.toLowerCase());
    return matchesText && (region === "all" || row.region === region);
  }).sort((a, b) => sort === "revenue" ? b.revenue - a.revenue : a.orderId - b.orderId), [query, region, sort]);

  const rows = filtered.slice((page - 1) * pageSize, page * pageSize);
  const totalRevenue = filtered.reduce((sum, row) => sum + row.revenue, 0);
  const regionTotals = filtered.reduce<Record<string, number>>((totals, row) => ({ ...totals, [row.region]: (totals[row.region] ?? 0) + row.revenue }), {});
  const maxRegionTotal = Math.max(...Object.values(regionTotals), 1);

  function downloadCsv() {
    const csv = ["order_id,region,channel,revenue,orders", ...filtered.map((row) => `${row.orderId},${row.region},${row.channel},${row.revenue},${row.orders}`)].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "synthetic-sales-data.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="mt-8 rounded-2xl border border-[#0D9488]/30 bg-[#131F36] p-5" aria-labelledby="analysis-lab-title">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-300">Data Analysis Lab</p>
          <h2 id="analysis-lab-title" className="mt-1 text-lg font-semibold text-white">{title}</h2>
          <p className="mt-2 text-sm text-slate-300">Interactive practice uses synthetic sales data only. SQL and Python execution are disabled; use the displayed query and local instructions for runnable work.</p>
        </div>
        <button type="button" onClick={downloadCsv} className="rounded-lg bg-[#0D9488] px-3 py-2 text-sm font-medium text-white hover:bg-teal-500">Download CSV</button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3"><p className="text-xs text-slate-400">Rows</p><p className="mt-1 text-xl font-semibold text-white">{filtered.length}</p></div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3"><p className="text-xs text-slate-400">Revenue</p><p className="mt-1 text-xl font-semibold text-white">${totalRevenue.toLocaleString()}</p></div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3"><p className="text-xs text-slate-400">Missing values</p><p className="mt-1 text-xl font-semibold text-white">0</p></div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
        <label className="text-sm text-slate-300">Search
          <input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="region, channel, order" className="mt-1 w-full rounded-lg border border-white/10 bg-[#0B1020] px-3 py-2 text-white outline-none focus:border-teal-400" />
        </label>
        <label className="text-sm text-slate-300">Region
          <select value={region} onChange={(event) => { setRegion(event.target.value); setPage(1); }} className="mt-1 w-full rounded-lg border border-white/10 bg-[#0B1020] px-3 py-2 text-white">
            <option value="all">All regions</option><option value="North">North</option><option value="South">South</option><option value="East">East</option><option value="West">West</option>
          </select>
        </label>
        <label className="text-sm text-slate-300">Sort
          <select value={sort} onChange={(event) => { setSort(event.target.value as "orderId" | "revenue"); setPage(1); }} className="mt-1 w-full rounded-lg border border-white/10 bg-[#0B1020] px-3 py-2 text-white">
            <option value="orderId">Order ID</option><option value="revenue">Revenue</option>
          </select>
        </label>
      </div>

      <div className="mt-5 overflow-x-auto rounded-xl border border-white/10">
        <table className="min-w-full text-left text-sm"><caption className="sr-only">Synthetic sales dataset</caption><thead className="bg-white/[0.04] text-slate-300"><tr>{["Order ID", "Region", "Channel", "Revenue", "Orders"].map((heading) => <th key={heading} className="px-3 py-2 font-medium">{heading}</th>)}</tr></thead><tbody>{rows.map((row) => <tr key={row.orderId} className="border-t border-white/10 text-slate-200"><td className="px-3 py-2">{row.orderId}</td><td className="px-3 py-2">{row.region}</td><td className="px-3 py-2">{row.channel}</td><td className="px-3 py-2">${row.revenue.toLocaleString()}</td><td className="px-3 py-2">{row.orders}</td></tr>)}</tbody></table>
      </div>
      <div className="mt-3 flex items-center justify-between text-sm text-slate-400"><span>Page {page} of {Math.max(1, Math.ceil(filtered.length / pageSize))}</span><div className="flex gap-2"><button type="button" disabled={page === 1} onClick={() => setPage((value) => value - 1)} className="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-40">Previous</button><button type="button" disabled={page >= Math.ceil(filtered.length / pageSize)} onClick={() => setPage((value) => value + 1)} className="rounded-lg border border-white/10 px-3 py-1.5 disabled:opacity-40">Next</button></div></div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <div><h3 className="font-medium text-white">Revenue by region</h3><div className="mt-3 space-y-3">{Object.entries(regionTotals).map(([name, value]) => <div key={name}><div className="mb-1 flex justify-between text-xs text-slate-300"><span>{name}</span><span>${value.toLocaleString()}</span></div><div className="h-3 rounded-full bg-white/10"><div className="h-3 rounded-full bg-teal-400" style={{ width: `${(value / maxRegionTotal) * 100}%` }} /></div></div>)}</div></div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4"><h3 className="font-medium text-white">SQL example</h3><pre className="mt-2 overflow-auto text-xs leading-6 text-slate-300"><code>{"SELECT region, SUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC;"}</code></pre><p className="mt-3 text-xs text-slate-400">Run locally against a disposable sample database only. The platform does not execute this query.</p></div>
      </div>
    </section>
  );
}
