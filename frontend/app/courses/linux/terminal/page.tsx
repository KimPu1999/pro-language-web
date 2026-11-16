"use client";

import Link from "next/link";
import { RefreshCw, Terminal as TerminalIcon } from "lucide-react";
import { useState } from "react";

type Vfs = { cwd: string; files: Record<string, string>; history: string[] };
const initial: Vfs = { cwd: "/", files: { "/README.txt": "Welcome to the simulated Linux lab.\n", "/home/student/notes.txt": "Practice safely.\n" }, history: [] };
const commands = ["pwd", "ls", "cd /home/student", "mkdir /home/student/lab", "touch /home/student/lab/todo.txt", "echo hello", "cat /home/student/notes.txt", "whoami", "history", "clear"];

function listFiles(files: Record<string, string>, cwd: string) {
  const prefix = cwd === "/" ? "/" : cwd + "/";
  return Object.keys(files).filter(path => path.startsWith(prefix)).map(path => path.slice(prefix.length).split("/")[0]).filter((value, index, values) => value && values.indexOf(value) === index).join("  ") || "(empty)";
}

export default function LinuxTerminalPage() {
  const [state, setState] = useState(initial);
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("Simulated Linux terminal. Type a supported command or choose a challenge.");
  function run(raw: string) {
    const command = raw.trim();
    if (!command) return;
    setState(previous => {
      const next = { cwd: previous.cwd, files: { ...previous.files }, history: [...previous.history, command] };
      const parts = command.split(/\s+/);
      if (command === "pwd") setOutput(next.cwd);
      else if (command === "ls" || command === "ls -la") setOutput(listFiles(next.files, next.cwd));
      else if (parts[0] === "cd") { const target = parts[1] || "/"; next.cwd = target.startsWith("/") ? target : next.cwd + "/" + target; setOutput("Changed directory to " + next.cwd); }
      else if (parts[0] === "mkdir") { const path = parts[1] || "/lab"; next.files[path + "/.directory"] = ""; setOutput("Created directory " + path); }
      else if (parts[0] === "touch") { const path = parts[1] || next.cwd + "/new.txt"; next.files[path] = ""; setOutput("Created file " + path); }
      else if (parts[0] === "echo") setOutput(parts.slice(1).join(" ") || "");
      else if (parts[0] === "cat") setOutput(next.files[parts[1]] ?? "cat: file not found");
      else if (command === "whoami") setOutput("student");
      else if (command === "history") setOutput(next.history.map((item, index) => (index + 1) + "  " + item).join("\n"));
      else if (command === "clear") setOutput("");
      else setOutput("Simulated: command not supported in this lesson.");
      return next;
    });
    setInput("");
  }
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/linux" className="text-sm text-amber-300 hover:text-white">← Back to Linux course</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300">Linux terminal</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Stateful virtual terminal</h1><p className="mt-4 text-lg leading-8 text-slate-400">Practice safe filesystem navigation in a browser-only virtual environment.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.75fr_1.25fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-amber-300"><TerminalIcon size={20}/><h2 className="font-semibold">Guided commands</h2></div><div className="mt-4 space-y-2">{commands.map(command => <button key={command} onClick={() => run(command)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left font-mono text-xs text-slate-300 hover:bg-amber-500/10 hover:text-amber-200">{command}</button>)}</div><button onClick={() => { setState(initial); setOutput("Simulation reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset environment</button></div><div className="space-y-5"><div className="rounded-2xl border border-amber-400/20 bg-[#080d16] p-5"><p className="text-xs uppercase tracking-wider text-amber-300">student@linux:{state.cwd}$</p><pre className="mt-3 min-h-28 whitespace-pre-wrap text-sm leading-7 text-amber-100"><code>{output}</code></pre><form onSubmit={event => { event.preventDefault(); run(input); }} className="mt-4 flex gap-2"><input value={input} onChange={event => setInput(event.target.value)} placeholder="Try pwd or ls" className="min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 font-mono text-sm text-white outline-none focus:border-amber-400"/><button className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white">Run</button></form></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Virtual filesystem</p><pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300"><code>{Object.keys(state.files).join("\n")}</code></pre></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Only predefined commands modify the in-memory virtual filesystem. No shell, host filesystem, network, production credential, or arbitrary command execution is available.</p></section>;
}
