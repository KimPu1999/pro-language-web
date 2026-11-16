"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

const responses: Record<string, string> = {
  "ip": "1: lo UP 127.0.0.1/8\n2: eth0 UP 192.0.2.10/24",
  "ifconfig": "eth0: flags=UP  inet 192.0.2.10  netmask 255.255.255.0",
  "ip route": "default via 192.0.2.1 dev eth0\n192.0.2.0/24 dev eth0",
  "nslookup academy.invalid": "Server: 192.0.2.53\nName: academy.invalid\nAddress: 192.0.2.20",
  "ping 192.0.2.20": "PING 192.0.2.20: 4 simulated replies, 0% loss",
  "traceroute 192.0.2.20": "1 192.0.2.1\n2 192.0.2.20\nComplete (simulated)"
};

export default function NetworkPlaygroundPage() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("Select a supported read-only command. This is an educational network simulator.");
  const [history, setHistory] = useState<string[]>([]);
  const run = (command: string) => { const value = command.trim(); setInput(value); if (!value) return; setHistory(current => [value, ...current].slice(0, 8)); setOutput(responses[value] ?? "Unsupported command. Try ip, ifconfig, ip route, nslookup academy.invalid, ping 192.0.2.20, or traceroute 192.0.2.20."); };
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/networking-fundamentals" className="text-sm text-sky-300 hover:text-white">← Back to Networking Fundamentals</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Educational network simulator</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Practice network commands safely</h1><p className="mt-4 text-lg leading-8 text-slate-400">Inspect simulated interfaces, routes, DNS, ping, and traceroute without touching a real network.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-sky-300"><Terminal size={20}/><h2 className="font-semibold">Supported commands</h2></div><div className="mt-4 space-y-2">{Object.keys(responses).map(command => <button key={command} onClick={() => run(command)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left font-mono text-xs text-slate-300 hover:bg-sky-500/10 hover:text-sky-200">{command}</button>)}</div><button onClick={() => { setHistory([]); setInput(""); setOutput("Simulator reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset environment</button></div><div className="space-y-5"><div className="rounded-2xl border border-sky-400/20 bg-[#07131d] p-5"><p className="text-xs uppercase tracking-wider text-sky-300">student@network:~$</p><form onSubmit={event => { event.preventDefault(); run(input); }} className="mt-3 flex gap-2"><input value={input} onChange={event => setInput(event.target.value)} placeholder="ip route" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 font-mono text-sm text-white outline-none focus:border-sky-400"/><button className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white">Run</button></form><pre className="mt-4 min-h-32 whitespace-pre-wrap text-sm leading-7 text-sky-100"><code>{output}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Command history</p><p className="mt-3 text-sm text-slate-300">{history.length ? history.join(" · ") : "empty"}</p></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Only predefined simulated responses are available. No host networking, shell, packet capture, private infrastructure, or unauthorized scanning is accessible.</p></section>;
}

