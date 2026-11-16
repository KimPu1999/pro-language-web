"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

const initialRows = [{ id: 1, title: "MySQL Foundations", published: true }, { id: 2, title: "Query Design", published: false }];
const queries: Record<string, string> = {
  "SHOW TABLES": "courses",
  "SELECT id, title FROM courses": "1 | MySQL Foundations\n2 | Query Design",
  "SELECT COUNT(*) FROM courses WHERE published = TRUE": "1",
  "UPDATE courses SET published = TRUE WHERE id = 2": "Query OK, 1 row affected (simulated)",
  "INSERT INTO courses (id, title) VALUES (3, 'Indexes')": "Query OK, 1 row affected (simulated)"
};

export default function MySQLPlaygroundPage() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("Select a supported query. This is an isolated in-memory simulation.");
  const [rows, setRows] = useState(initialRows);
  const [history, setHistory] = useState<string[]>([]);
  const run = (query: string) => { const value = query.trim(); setInput(value); if (!value) return; setHistory(current => [value, ...current].slice(0, 8)); if (value.startsWith("UPDATE")) setRows(current => current.map(row => row.id === 2 ? { ...row, published: true } : row)); if (value.startsWith("INSERT")) setRows(current => current.some(row => row.id === 3) ? current : [...current, { id: 3, title: "Indexes", published: false }]); setOutput(queries[value] ?? "Unsupported query. Try SHOW TABLES, SELECT, UPDATE, or INSERT examples."); };
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/mysql" className="text-sm text-cyan-300 hover:text-white">← Back to MySQL</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">SQL playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Safe MySQL query simulator</h1><p className="mt-4 text-lg leading-8 text-slate-400">Practice supported SQL reads and writes against a local virtual courses table.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-cyan-300"><Terminal size={20}/><h2 className="font-semibold">Supported queries</h2></div><div className="mt-4 space-y-2">{Object.keys(queries).map(query => <button key={query} onClick={() => run(query)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left font-mono text-xs text-slate-300 hover:bg-cyan-500/10 hover:text-cyan-200">{query}</button>)}</div><button onClick={() => { setRows(initialRows); setHistory([]); setInput(""); setOutput("Simulation reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset database</button></div><div className="space-y-5"><div className="rounded-2xl border border-cyan-400/20 bg-[#06141a] p-5"><p className="text-xs uppercase tracking-wider text-cyan-300">mysql&gt; simulator</p><form onSubmit={event => { event.preventDefault(); run(input); }} className="mt-3 flex gap-2"><input value={input} onChange={event => setInput(event.target.value)} placeholder="SELECT id, title FROM courses" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 font-mono text-sm text-white outline-none focus:border-cyan-400"/><button className="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white">Run</button></form><pre className="mt-4 min-h-28 whitespace-pre-wrap text-sm leading-7 text-cyan-100"><code>{output}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Virtual courses table</p><div className="mt-3 overflow-x-auto"><table className="w-full min-w-[420px] text-left text-sm"><thead className="text-slate-500"><tr><th className="px-2 py-2">id</th><th className="px-2 py-2">title</th><th className="px-2 py-2">published</th></tr></thead><tbody>{rows.map(row => <tr key={row.id} className="border-t border-line text-slate-300"><td className="px-2 py-2">{row.id}</td><td className="px-2 py-2">{row.title}</td><td className="px-2 py-2">{String(row.published)}</td></tr>)}</tbody></table></div><p className="mt-4 text-xs text-slate-500">History: {history.length ? history.join(" · ") : "empty"}</p></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Only predefined queries modify in-memory state. No MySQL server, platform PostgreSQL, filesystem, network, or untrusted SQL execution is available.</p></section>;
}

