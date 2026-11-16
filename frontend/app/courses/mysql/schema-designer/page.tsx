"use client";

import Link from "next/link";
import { RefreshCw, Sparkles } from "lucide-react";
import { useState } from "react";

type Column = { name: string; type: string; key: string };
const initialColumns: Column[] = [{ name: "id", type: "BIGINT", key: "PRIMARY KEY" }, { name: "title", type: "VARCHAR(120)", key: "NOT NULL" }];
const types = ["VARCHAR(120)", "INT", "BIGINT", "BOOLEAN", "DATETIME", "TEXT"];
export default function MySQLSchemaDesignerPage() {
  const [columns, setColumns] = useState(initialColumns);
  const [name, setName] = useState("");
  const [type, setType] = useState(types[0]);
  const addColumn = () => { const value = name.trim(); if (!value || columns.some(column => column.name === value)) return; setColumns(current => [...current, { name: value, type, key: "" }]); setName(""); };
  const reset = () => { setColumns(initialColumns); setName(""); setType(types[0]); };
  const sql = "CREATE TABLE courses (\n" + columns.map(column => "  " + column.name + " " + column.type + (column.key ? " " + column.key : "")).join(",\n") + "\n);";
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/mysql" className="text-sm text-cyan-300 hover:text-white">← Back to MySQL</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">ER diagram designer</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Design a relational table</h1><p className="mt-4 text-lg leading-8 text-slate-400">Add columns, preview CREATE TABLE SQL, and reason about keys and constraints locally.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[1fr_.9fr]"><div className="rounded-2xl border border-line bg-surface p-5 sm:p-7"><div className="flex flex-wrap gap-2"><input value={name} onChange={event => setName(event.target.value)} placeholder="column name" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white outline-none focus:border-cyan-400"/><select value={type} onChange={event => setType(event.target.value)} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white">{types.map(value => <option key={value}>{value}</option>)}</select><button onClick={addColumn} className="inline-flex items-center gap-2 rounded-lg bg-cyan-600 px-3 py-2 text-sm font-semibold text-white"><Sparkles size={15}/> Add</button></div><div className="mt-6 space-y-2">{columns.map(column => <div key={column.name} className="flex items-center justify-between rounded-xl bg-ink/60 p-4"><span className="font-mono text-sm text-white">{column.name}</span><span className="text-xs text-cyan-300">{column.type}{column.key ? " · " + column.key : ""}</span></div>)}</div><button onClick={reset} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset designer</button></div><aside className="rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-5 sm:p-7"><div className="flex items-center gap-3 text-cyan-300"><Sparkles size={20}/><h2 className="font-semibold">CREATE TABLE preview</h2></div><pre className="mt-5 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-cyan-100"><code>{sql}</code></pre><p className="mt-5 text-xs leading-5 text-cyan-100">Add foreign keys and relationship tables when modeling one-to-many or many-to-many data.</p></aside></div></section>;
}

