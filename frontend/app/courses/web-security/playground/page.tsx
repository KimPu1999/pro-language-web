"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

const examples = [
  { name: "SQL query boundary", language: "Python", unsafe: "query = \"SELECT * FROM users WHERE id = '\" + user_id + \"'\"", safe: "query = \"SELECT * FROM users WHERE id = %s\"", output: "Use a parameterized query; never concatenate untrusted input." },
  { name: "HTML output boundary", language: "JavaScript", unsafe: "element.innerHTML = userComment", safe: "element.textContent = userComment", output: "Render untrusted text as text unless trusted HTML is explicitly required." },
  { name: "Server authorization", language: "TypeScript", unsafe: "if (userId === requestedUserId) return record", safe: "return authorizeServerSide(session, record.ownerId)", output: "Authorize the requested object on the server, not only from client claims." }
];

export default function SecurityPlaygroundPage() {
  const [selected, setSelected] = useState(0);
  const example = examples[selected];
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/web-security" className="text-sm text-red-300 hover:text-white">← Back to Web Security</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">Secure coding playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Compare safe patterns</h1><p className="mt-4 text-lg leading-8 text-slate-400">Inspect predefined defensive examples and the root cause each secure pattern addresses.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.75fr_1.25fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-red-300"><Terminal size={20}/><h2 className="font-semibold">Examples</h2></div><div className="mt-4 space-y-2">{examples.map((item, index) => <button key={item.name} onClick={() => setSelected(index)} className={"block w-full rounded-lg px-3 py-2 text-left text-sm " + (index === selected ? "bg-red-500/15 text-red-100" : "bg-ink text-slate-300 hover:bg-white/5")}>{item.name}</button>)}</div><button onClick={() => setSelected(0)} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div><div className="space-y-5"><div className="rounded-2xl border border-red-400/20 bg-[#160b12] p-5"><p className="text-xs uppercase tracking-wider text-red-300">Unsafe pattern for review · {example.language}</p><pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-red-100"><code>{example.unsafe}</code></pre></div><div className="rounded-2xl border border-emerald-400/20 bg-[#071711] p-5"><p className="text-xs uppercase tracking-wider text-emerald-300">Secure pattern</p><pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-emerald-100"><code>{example.safe}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Remediation</p><p className="mt-3 text-sm leading-7 text-slate-300">{example.output}</p></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Predefined code comparison only. No arbitrary code execution, external scanning, host filesystem access, or public-target testing is available.</p></section>;
}

