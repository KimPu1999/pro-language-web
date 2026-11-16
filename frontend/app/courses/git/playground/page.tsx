"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

type SimState = { working: string[]; staged: string[]; commits: string[]; branch: string };
const initial: SimState = { working: ["README.md"], staged: [], commits: [], branch: "main" };
const commands = ["git init", "git status", "git add README.md", "git commit -m \"Add README\"", "git log --oneline", "git branch feature", "git switch feature", "git merge main", "git restore README.md", "git reset", "git stash"];

export default function GitPlaygroundPage() {
  const [state, setState] = useState(initial);
  const [output, setOutput] = useState("Choose a predefined command to inspect the simulated repository.");
  function run(command: string) {
    setState(previous => {
      const next = { ...previous, working: [...previous.working], staged: [...previous.staged], commits: [...previous.commits] };
      if (command === "git add README.md") { next.staged = ["README.md"]; setOutput("README.md staged for the next commit."); }
      else if (command.startsWith("git commit")) { next.commits.unshift(`${next.commits.length + 1} Add README`); next.working = []; next.staged = []; setOutput("[main] Add README\n1 file changed"); }
      else if (command === "git status") setOutput(next.working.length ? `Changes not staged: ${next.working.join(", ")}` : "working tree clean");
      else if (command === "git log --oneline") setOutput(next.commits.join("\n") || "No commits yet");
      else if (command === "git branch feature") setOutput("Created branch feature (simulated).");
      else if (command === "git switch feature") { next.branch = "feature"; setOutput("Switched to branch 'feature' (simulated)."); }
      else if (command === "git stash") { next.working = []; setOutput("Saved working directory state to simulated stash."); }
      else if (command === "git restore README.md") { next.working = []; setOutput("Restored README.md from the simulated index."); }
      else if (command === "git reset") { next.staged = []; setOutput("Unstaged simulated changes; commit history unchanged."); }
      else setOutput(`${command}\nSimulated command completed; inspect the state cards.`);
      return next;
    });
  }
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/git" className="text-sm text-orange-300 hover:text-white">← Back to Git course</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-orange-300">Git playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Simulated Git terminal</h1><p className="mt-4 text-lg leading-8 text-slate-400">Choose predefined commands and watch a virtual repository change. This is not a real Git process.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-orange-300"><Terminal size={20} /><h2 className="font-semibold">Commands</h2></div><div className="mt-4 space-y-2">{commands.map(command => <button key={command} onClick={() => run(command)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left font-mono text-xs text-slate-300 hover:bg-orange-500/10 hover:text-orange-200">{command}</button>)}</div><button onClick={() => { setState(initial); setOutput("Simulation reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15} /> Reset simulation</button></div><div className="space-y-5"><div className="rounded-2xl border border-orange-400/20 bg-[#0a1220] p-5"><p className="text-xs uppercase tracking-wider text-orange-300">Simulated output</p><pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-orange-100"><code>{output}</code></pre></div><div className="grid gap-4 sm:grid-cols-2"><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs text-slate-500">Working tree</p><p className="mt-3 text-sm text-slate-200">{state.working.join(", ") || "clean"}</p></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs text-slate-500">Staging area</p><p className="mt-3 text-sm text-slate-200">{state.staged.join(", ") || "empty"}</p></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs text-slate-500">Branch</p><p className="mt-3 text-sm text-slate-200">{state.branch}</p></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs text-slate-500">Commit history</p><p className="mt-3 whitespace-pre-wrap text-sm text-slate-200">{state.commits.join("\n") || "empty"}</p></div></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Commands are predefined and state is in-memory in your browser. No shell, filesystem, remote, or arbitrary command execution is available.</p></section>;
}
