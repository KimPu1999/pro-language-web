"use client";

import Link from "next/link";
import { RefreshCw, Sparkles } from "lucide-react";
import { useState } from "react";

type Field = { name: string; type: string; required: boolean };
const initialFields: Field[] = [{ name: "title", type: "string", required: true }, { name: "done", type: "boolean", required: true }];
const types = ["string", "number", "boolean", "date", "objectId", "array"];
export default function MongoSchemaDesignerPage() {
  const [fields, setFields] = useState(initialFields);
  const [name, setName] = useState("");
  const [type, setType] = useState("string");
  const addField = () => { const value = name.trim(); if (!value || fields.some(field => field.name === value)) return; setFields(current => [...current, { name: value, type, required: false }]); setName(""); };
  const reset = () => { setFields(initialFields); setName(""); setType("string"); };
  const preview = Object.fromEntries(fields.map(field => [field.name, field.type === "boolean" ? false : field.type === "number" ? 0 : field.type === "array" ? [] : field.type === "objectId" ? "ObjectId(\"simulated\")" : field.type === "date" ? "ISODate(\"2026-01-01\")" : "example"]));
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/mongodb" className="text-sm text-emerald-300 hover:text-white">← Back to MongoDB</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">Schema designer</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Model a document locally</h1><p className="mt-4 text-lg leading-8 text-slate-400">Add fields, preview BSON-like values, and reason about validation without modifying a real database.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[1fr_.9fr]"><div className="rounded-2xl border border-line bg-surface p-5 sm:p-7"><div className="flex flex-wrap gap-2"><input value={name} onChange={event => setName(event.target.value)} placeholder="field name" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white outline-none focus:border-emerald-400"/><select value={type} onChange={event => setType(event.target.value)} className="rounded-lg border border-line bg-ink px-3 py-2 text-sm text-white">{types.map(value => <option key={value}>{value}</option>)}</select><button onClick={addField} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white"><Sparkles size={15}/> Add</button></div><div className="mt-6 space-y-2">{fields.map(field => <div key={field.name} className="flex items-center justify-between rounded-xl bg-ink/60 p-4"><span className="font-mono text-sm text-white">{field.name}</span><span className="text-xs text-emerald-300">{field.type}{field.required ? " · required" : ""}</span></div>)}</div><button onClick={reset} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset designer</button></div><aside className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-5 sm:p-7"><div className="flex items-center gap-3 text-emerald-300"><Sparkles size={20}/><h2 className="font-semibold">Document preview</h2></div><pre className="mt-5 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-emerald-100"><code>{JSON.stringify(preview, null, 2)}</code></pre><p className="mt-5 text-xs leading-5 text-emerald-100">Use access patterns, cardinality, validation, and index requirements to refine this model.</p></aside></div></section>;
}

