"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Category = { id: string; name: string; slug: string; description: string };
type Tool = { id: string; name: string; slug: string; short_description: string; full_description: string; icon_key: string; route_path: string; tags: string[]; is_featured: boolean; category?: Category | null; implementation: string; implementation_available: boolean };
type Page = { items: Tool[]; page: number; page_size: number; total: number; pages: number };

const iconLabels: Record<string, string> = { braces: "{}", check: "✓", binary: "01", fingerprint: "ID", code: "</>" };

export function ToolsCatalog() {
  const [data, setData] = useState<Page | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  useEffect(() => { fetch("/api/v1/tools/categories").then(r => r.ok ? r.json() : []).then(setCategories).catch(() => setCategories([])); }, []);
  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), page_size: "12" });
    if (search) params.set("search", search); if (category) params.set("category", category);
    setData(null); setError("");
    fetch(`/api/v1/tools?${params}`).then(r => r.ok ? r.json() : Promise.reject(new Error("The tools catalog is temporarily unavailable."))).then(setData).catch(reason => setError(reason instanceof Error ? reason.message : "Unable to load developer tools."));
  }, [search, category, page]);
  const featured = useMemo(() => data?.items.filter(tool => tool.is_featured) ?? [], [data]);
  return <section className="mx-auto max-w-6xl px-6 py-14 sm:py-20">
    <div className="rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-500/20 via-surface to-surface p-7 sm:p-10"><p className="text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Developer tools</p><h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">Small utilities for everyday development.</h1><p className="mt-5 max-w-2xl leading-8 text-slate-300">Format, inspect, convert, and validate common developer data locally in your browser. Sensitive input stays in this browser tab.</p></div>
    <form onSubmit={event => { event.preventDefault(); setPage(1); setSearch(query.trim()); }} className="mt-8 flex flex-col gap-3 sm:flex-row"><input aria-label="Search developer tools" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search JSON, encoding, security…" className="h-11 flex-1 rounded-xl border border-line bg-surface px-4 text-sm outline-none focus:border-indigo-400" /><select aria-label="Filter tool category" value={category} onChange={event => { setPage(1); setCategory(event.target.value); }} className="h-11 rounded-xl border border-line bg-surface px-4 text-sm outline-none focus:border-indigo-400"><option value="">All categories</option>{categories.map(item => <option key={item.slug} value={item.slug}>{item.name}</option>)}</select><button className="h-11 rounded-xl bg-primary px-5 text-sm font-semibold hover:bg-indigo-500">Search</button></form>
    {error && <p role="alert" className="mt-8 rounded-xl border border-red-400/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</p>}
    {!data && !error && <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3, 4, 5, 6].map(item => <div key={item} className="h-48 animate-pulse rounded-2xl border border-line bg-surface" />)}</div>}
    {data && featured.length > 0 && <><p className="mt-10 text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">Featured tools</p><div className="mt-4 grid gap-4 md:grid-cols-2">{featured.map(tool => <ToolCard key={tool.id} tool={tool} />)}</div></>}
    {data && <><p className="mt-10 text-sm font-semibold uppercase tracking-[.18em] text-indigo-300">All tools <span className="text-slate-500">({data.total})</span></p><div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{data.items.map(tool => <ToolCard key={tool.id} tool={tool} />)}{data.items.length === 0 && <p className="rounded-xl border border-line bg-surface p-6 text-slate-400 sm:col-span-2 lg:col-span-3">No published tools match your filters.</p>}</div><Pagination data={data} page={page} setPage={setPage} /></>}
  </section>;
}

function ToolCard({ tool }: { tool: Tool }) { return <Link href={tool.route_path} className="group rounded-2xl border border-line bg-surface p-5 transition hover:-translate-y-0.5 hover:border-indigo-400/60"><div className="flex items-start justify-between gap-4"><span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/15 font-mono text-sm font-bold text-indigo-300">{iconLabels[tool.icon_key] ?? "*"}</span><span className="rounded-full bg-white/[.05] px-2 py-1 text-xs text-slate-400">{tool.category?.name ?? "Tools"}</span></div><h2 className="mt-5 font-semibold group-hover:text-indigo-200">{tool.name}</h2><p className="mt-2 min-h-12 text-sm leading-6 text-slate-400">{tool.short_description}</p><div className="mt-4 flex flex-wrap gap-2">{tool.tags.map(tag => <span key={tag} className="rounded-full border border-line px-2 py-1 text-[11px] text-slate-500">{tag}</span>)}</div><span className="mt-5 block text-xs font-semibold text-indigo-300">Open tool →</span></Link>; }
function Pagination({ data, page, setPage }: { data: Page; page: number; setPage: (value: number) => void }) { return data.pages > 1 ? <div className="mt-8 flex items-center justify-between text-sm text-slate-400"><button disabled={page <= 1} onClick={() => setPage(page - 1)} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Previous</button><span>Page {page} of {data.pages}</span><button disabled={page >= data.pages} onClick={() => setPage(page + 1)} className="rounded-lg border border-line px-3 py-2 disabled:opacity-40">Next</button></div> : null; }

export function ToolDetail({ slug }: { slug: string }) {
  const [tool, setTool] = useState<Tool | null>(null); const [error, setError] = useState("");
  useEffect(() => { fetch(`/api/v1/tools/${encodeURIComponent(slug)}`).then(r => r.ok ? r.json() : Promise.reject(new Error("Published developer tool not found."))).then(setTool).catch(reason => setError(reason instanceof Error ? reason.message : "Unable to load this tool.")); }, [slug]);
  if (error) return <section className="mx-auto max-w-3xl px-6 py-20"><div className="rounded-2xl border border-line bg-surface p-8"><h1 className="text-2xl font-bold">Tool unavailable</h1><p className="mt-3 text-slate-400">{error}</p><Link className="mt-6 inline-block text-indigo-300" href="/tools">← Back to tools</Link></div></section>;
  if (!tool) return <section className="mx-auto max-w-5xl px-6 py-20"><div className="h-72 animate-pulse rounded-2xl border border-line bg-surface" /></section>;
  return <section className="mx-auto max-w-5xl px-6 py-14 sm:py-20"><Link href="/tools" className="text-sm text-indigo-300 hover:text-white">← All developer tools</Link><div className="mt-6 flex items-start gap-4"><span className="grid h-12 w-12 place-items-center rounded-xl bg-indigo-500/15 font-mono font-bold text-indigo-300">{iconLabels[tool.icon_key] ?? "*"}</span><div><p className="text-sm text-indigo-300">{tool.category?.name ?? "Developer tool"}</p><h1 className="mt-1 text-3xl font-bold">{tool.name}</h1><p className="mt-2 text-slate-400">{tool.full_description || tool.short_description}</p></div></div><ToolWorkbench implementation={tool.implementation} name={tool.name} /><p className="mt-4 text-xs leading-5 text-slate-500">Runs locally in your browser. Do not paste passwords, tokens, private keys, or personal data.</p></section>;
}

function ToolWorkbench({ implementation, name }: { implementation: string; name: string }) {
  const [value, setValue] = useState(""); const [output, setOutput] = useState("");
  const run = () => { try {
    if (implementation === "json_formatter" || implementation === "json_validator") { const parsed = JSON.parse(value); setOutput(implementation === "json_formatter" ? JSON.stringify(parsed, null, 2) : "Valid JSON"); }
    else if (implementation === "base64_encoder") { setOutput(value ? btoa(unescape(encodeURIComponent(value))) : ""); }
    else if (implementation === "uuid_generator") { setOutput(crypto.randomUUID()); }
    else if (implementation === "code_playground") { setOutput("Use this browser-safe workspace to draft code. Server-side arbitrary execution is disabled by design."); }
    else { setOutput(value); }
  } catch (reason) { setOutput(reason instanceof Error ? `Invalid input: ${reason.message}` : "Invalid input"); } };
  return <div className="mt-8 rounded-2xl border border-line bg-surface p-5 sm:p-6"><textarea aria-label={`${name} input`} value={value} onChange={event => setValue(event.target.value)} placeholder={implementation === "json_formatter" ? '{"language":"typescript"}' : `Enter input for ${name}`} className="min-h-56 w-full rounded-xl border border-line bg-ink p-4 font-mono text-sm text-slate-100 outline-none focus:border-indigo-400" /><div className="mt-4 flex flex-wrap gap-2"><button type="button" onClick={run} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold hover:bg-indigo-500">Run locally</button><button type="button" onClick={() => { setValue(""); setOutput(""); }} className="rounded-xl border border-line px-4 py-2.5 text-sm text-slate-300 hover:bg-white/[.05]">Clear</button></div>{output && <pre className="mt-5 max-h-96 overflow-auto rounded-xl bg-[#0a0f1c] p-4 text-sm leading-6 text-emerald-200" aria-live="polite">{output}</pre>}</div>;
}
