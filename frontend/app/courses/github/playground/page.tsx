"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";

type SimState = { branch: string; commits: string[]; pullRequest: string; checks: string; issues: number };
const initial: SimState = { branch: "main", commits: ["Initial commit"], pullRequest: "none", checks: "not run", issues: 0 };
const actions = ["Create feature branch", "Push feature branch", "Open pull request", "Run checks", "Request review", "Merge pull request", "Create issue"];

export default function GitHubPlaygroundPage() {
  const [state, setState] = useState(initial);
  const [output, setOutput] = useState("Choose a predefined workflow action to inspect the simulated repository.");
  function run(action: string) {
    setState(previous => {
      const next = { ...previous, commits: [...previous.commits] };
      if (action === "Create feature branch") { next.branch = "feature/readme"; setOutput("Created feature/readme (simulated)."); }
      else if (action === "Push feature branch") setOutput("Pushed feature/readme to the simulated remote.");
      else if (action === "Open pull request") { next.pullRequest = "open"; setOutput("Pull request #1 opened against main."); }
      else if (action === "Run checks") { next.checks = "passed"; setOutput("lint, test, and security checks passed (simulated)."); }
      else if (action === "Request review") setOutput("Review requested from the simulated team.");
      else if (action === "Merge pull request") { next.branch = "main"; next.pullRequest = "merged"; next.commits.unshift("Merge pull request #1"); setOutput("Pull request merged into main (simulated)."); }
      else { next.issues += 1; setOutput("Created issue #" + next.issues + " with a safe placeholder."); }
      return next;
    });
  }
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/github" className="text-sm text-indigo-300 hover:text-white">← Back to GitHub course</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-300">GitHub playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Collaborative workflow simulator</h1><p className="mt-4 text-lg leading-8 text-slate-400">Practice branches, pull requests, checks, reviews, and issues using an in-memory scenario.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-indigo-300"><Terminal size={20}/><h2 className="font-semibold">Workflow actions</h2></div><div className="mt-4 space-y-2">{actions.map(action => <button key={action} onClick={() => run(action)} className="block w-full rounded-lg bg-ink px-3 py-2 text-left text-sm text-slate-300 hover:bg-indigo-500/10 hover:text-indigo-200">{action}</button>)}</div><button onClick={() => { setState(initial); setOutput("Simulation reset."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset simulation</button></div><div className="space-y-5"><div className="rounded-2xl border border-indigo-400/20 bg-[#0a1220] p-5"><p className="text-xs uppercase tracking-wider text-indigo-300">Simulated output</p><pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-indigo-100"><code>{output}</code></pre></div><div className="grid gap-4 sm:grid-cols-2">{[["Branch", state.branch], ["Pull request", state.pullRequest], ["Checks", state.checks], ["Issues", String(state.issues)], ["Commit history", state.commits.join("\n")]].map(([label, value]) => <div key={label} className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs text-slate-500">{label}</p><p className="mt-3 whitespace-pre-wrap text-sm text-slate-200">{value}</p></div>)}</div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">Actions are predefined and state is in-memory in your browser. No GitHub account, token, shell, filesystem, or real repository is accessed.</p></section>;
}
