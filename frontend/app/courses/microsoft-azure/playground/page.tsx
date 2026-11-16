"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

const commands: Record<string, string> = {
  "az version": "{\n  \"azure-cli\": \"simulated 2.x\"\n}",
  "az account show": "{ \"name\": \"CodeMaster Learning Subscription\", \"state\": \"Enabled (simulated)\" }",
  "az group list": "[ { \"name\": \"academy-learn-rg\", \"location\": \"eastus\" } ]",
  "az vm list": "[ ]  # No simulated VMs yet",
  "az storage account list": "[ ]  # No simulated storage yet",
  "az group create --name academy-learn-rg --location eastus": "{ \"provisioningState\": \"Succeeded (simulated)\", \"name\": \"academy-learn-rg\" }",
};

export default function AzurePlaygroundPage() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("Type or select a supported command. No real login or Azure request is made.");
  const [history, setHistory] = useState<string[]>([]);
  const run = (command: string) => { const trimmed = command.trim(); setInput(trimmed); if (!trimmed) return; setHistory(current => [trimmed, ...current].slice(0, 8)); setOutput(commands[trimmed] ?? "Command not supported in this educational simulator. Try az version, az account show, az group list, az vm list, or az storage account list."); };
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/microsoft-azure" className="text-sm text-sky-300 hover:text-white">← Back to Microsoft Azure</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Azure CLI playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Practice safe Azure commands</h1><p className="mt-4 text-lg leading-8 text-slate-400">A browser-only command simulator with predefined outputs and no credential collection.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-sky-300"><Terminal size={20}/><h2 className="font-semibold">Supported commands</h2></div><div className="mt-4 space-y-2">{Object.keys(commands).map(command => <button key={command} onClick={() => run(command)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left font-mono text-xs text-slate-300 hover:bg-sky-500/10 hover:text-sky-200">{command}</button>)}</div><button onClick={() => { setHistory([]); setInput(""); setOutput("Simulation reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div><div className="space-y-5"><div className="rounded-2xl border border-sky-400/20 bg-[#07111d] p-5"><p className="text-xs uppercase tracking-wider text-sky-300">academy@azure:~$</p><form onSubmit={event => { event.preventDefault(); run(input); }} className="mt-3 flex gap-2"><input value={input} onChange={event => setInput(event.target.value)} placeholder="az account show" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 font-mono text-sm text-white outline-none focus:border-sky-400"/><button className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white">Run</button></form><pre className="mt-4 min-h-28 whitespace-pre-wrap text-sm leading-7 text-sky-100"><code>{output}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Command history</p><p className="mt-3 text-sm text-slate-300">{history.length ? history.join("\n") : "No commands run yet."}</p></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Only predefined commands and simulated outputs are available. No shell, network, Azure credential, filesystem, or real resource mutation is accessible.</p></section>;
}

