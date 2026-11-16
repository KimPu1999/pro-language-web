"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

const examples = [
  { name: "String + TTL", command: 'SET cache:course:42 "Redis" EX 60\nGET cache:course:42\nTTL cache:course:42', output: '"Redis"\n(integer) 60' },
  { name: "Hash record", command: 'HSET user:42 name Ada role student\nHGETALL user:42', output: '(integer) 2\nname\nAda\nrole\nstudent' },
  { name: "Queue list", command: 'LPUSH jobs:email job-1\nLPUSH jobs:email job-2\nLRANGE jobs:email 0 -1', output: '(integer) 1\n(integer) 2\njob-2\njob-1' },
  { name: "Sorted set", command: 'ZADD leaderboard 98 user-42\nZRANGE leaderboard 0 -1 WITHSCORES', output: '(integer) 1\nuser-42\n98' },
];

export default function RedisPlaygroundPage() {
  const [selected, setSelected] = useState(0);
  const example = examples[selected];
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8">
    <Link href="/courses/redis" className="text-sm text-slate-300 hover:text-white">← Back to Redis</Link>
    <div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">Redis CLI playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Practice Redis safely</h1><p className="mt-4 text-lg leading-8 text-slate-400">Explore predefined commands and deterministic replies without connecting to platform Redis.</p></div>
    <div className="mt-10 grid gap-6 lg:grid-cols-[.7fr_1.3fr]">
      <div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-red-300"><Terminal size={20}/><h2 className="font-semibold">Guided commands</h2></div><div className="mt-4 space-y-2">{examples.map((item, index) => <button key={item.name} onClick={() => setSelected(index)} className={`block w-full rounded-lg px-3 py-3 text-left text-sm ${index === selected ? "bg-red-500/20 text-white" : "bg-ink text-slate-300 hover:bg-white/5"}`}>{item.name}</button>)}</div><button onClick={() => setSelected(0)} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div>
      <div className="space-y-5"><div className="rounded-2xl border border-red-400/20 bg-[#1c1114] p-5"><p className="text-xs uppercase tracking-wider text-red-300">Simulated terminal</p><pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-red-100"><code>{`127.0.0.1:6379> ${example.command}`}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Deterministic output</p><pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-emerald-300"><code>{example.output}</code></pre></div></div>
    </div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Simulation only: commands are predefined and run in memory. No arbitrary command execution, platform Redis access, network proxy, or student credentials are available.</p>
  </section>;
}
