"use client";

import Link from "next/link";
import { ArrowRight, RefreshCw, Sparkles } from "lucide-react";
import { useState } from "react";

const steps = [
  { label: "HTTP request", detail: "A browser asks for /courses/ through an HTTP request." },
  { label: "URLconf", detail: "Django checks URL patterns from top to bottom and selects a matching view." },
  { label: "View", detail: "The view validates the request, applies application rules, and decides what data is needed." },
  { label: "Model / ORM", detail: "The view may query models through the ORM. Values must still be authorized for the current user." },
  { label: "Template", detail: "The template receives explicit context and renders presentation with auto-escaping enabled." },
  { label: "HTTP response", detail: "Django returns a response with status, headers, and HTML or JSON content." },
];

export default function DjangoVisualizerPage() {
  const [step, setStep] = useState(0);
  const current = steps[step];
  return (
    <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8">
      <Link href="/courses/django" className="text-sm text-emerald-300 hover:text-white">← Back to Django course</Link>
      <div className="mt-8 max-w-3xl">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">Django visualizer</p>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">MVT request lifecycle</h1>
        <p className="mt-4 text-lg leading-8 text-slate-400">Step through the path of a request from URL matching to a rendered response.</p>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-[1.1fr_.9fr]">
        <div className="rounded-2xl border border-emerald-400/20 bg-surface p-5 sm:p-7">
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-slate-400">Step {step + 1} of {steps.length}</span>
            <button onClick={() => setStep(0)} className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-xs text-slate-300 hover:border-emerald-400/50" aria-label="Reset visualizer"><RefreshCw size={14} /> Reset</button>
          </div>
          <div className="mt-8 grid gap-3 sm:grid-cols-3" role="list" aria-label="MVT request steps">
            {steps.map((item, index) => (
              <button key={item.label} onClick={() => setStep(index)} className={`rounded-xl p-4 text-left transition ${index === step ? "bg-emerald-500/20 text-emerald-100 ring-1 ring-emerald-400/50" : "bg-ink/60 text-slate-400 hover:bg-white/5"}`} aria-current={index === step ? "step" : undefined}>
                <span className="text-[11px] text-slate-500">0{index + 1}</span>
                <span className="mt-2 block text-sm font-semibold">{item.label}</span>
              </button>
            ))}
          </div>
          <div className="mt-8 rounded-xl bg-[#087F5B]/15 p-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">Current stage</p>
            <h2 className="mt-2 text-2xl font-bold text-white">{current.label}</h2>
            <p className="mt-3 leading-7 text-slate-300">{current.detail}</p>
          </div>
          <div className="mt-5 flex justify-between gap-3">
            <button onClick={() => setStep(value => Math.max(0, value - 1))} disabled={step === 0} className="inline-flex items-center gap-2 rounded-lg border border-line px-4 py-2 text-sm text-slate-300 disabled:opacity-40"><ArrowRight className="rotate-180" size={16} /> Previous</button>
            <button onClick={() => setStep(value => Math.min(steps.length - 1, value + 1))} disabled={step === steps.length - 1} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">Next <ArrowRight size={16} /></button>
          </div>
        </div>
        <aside className="rounded-2xl border border-line bg-surface p-5 sm:p-7">
          <div className="flex items-center gap-3 text-emerald-300"><Sparkles size={20} /><span className="font-semibold">Production reminder</span></div>
          <ul className="mt-5 space-y-4 text-sm leading-6 text-slate-400">
            <li>Authorize records on the server; never trust a user id from the browser.</li>
            <li>Keep secrets in environment variables or a secret manager.</li>
            <li>Use CSRF protection for state-changing browser forms.</li>
            <li>Use tests and logs to verify each boundary before deployment.</li>
          </ul>
          <p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">This is an instructional visualization. It does not execute a live Django application or student code.</p>
        </aside>
      </div>
    </section>
  );
}
