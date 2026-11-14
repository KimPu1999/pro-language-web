"use client";

import { useState } from "react";

export function DartPlayground({ title, code }: { title: string; code: string }) {
  const [copied, setCopied] = useState(false);

  async function copyCode() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  function downloadCode() {
    const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "main.dart";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="mt-8 rounded-2xl border border-[#0175C2]/30 bg-[#131F36] p-5" aria-labelledby="dart-practice-title">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#4DB6FF]">Dart practice</p>
          <h2 id="dart-practice-title" className="mt-1 text-lg font-semibold text-white">{title}</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-300">This lesson uses a safe, read-only example viewer. Hosted arbitrary Dart and Flutter execution is disabled until an isolated runner is verified.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={copyCode} className="rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-200 hover:bg-white/5">{copied ? "Copied" : "Copy"}</button>
          <button type="button" onClick={downloadCode} className="rounded-lg bg-[#0175C2] px-3 py-2 text-sm font-medium text-white hover:bg-[#0B84D1]">Download .dart</button>
        </div>
      </div>
      <pre className="mt-4 max-h-[28rem] overflow-auto rounded-xl border border-white/10 bg-[#0B1020] p-4 text-sm leading-6 text-slate-100" tabIndex={0}><code>{code}</code></pre>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <h3 className="font-medium text-white">Run locally</h3>
          <pre className="mt-2 overflow-auto text-xs leading-6 text-slate-300"><code>{"dart --version\ndart analyze\ndart run main.dart"}</code></pre>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <h3 className="font-medium text-white">Flutter lessons</h3>
          <pre className="mt-2 overflow-auto text-xs leading-6 text-slate-300"><code>{"flutter --version\nflutter doctor\nflutter pub get\nflutter run"}</code></pre>
        </div>
      </div>
      <p className="mt-4 text-xs text-slate-400">Pin exact Dart and Flutter SDK versions in the project README, pubspec.yaml, and CI before sharing a runnable project.</p>
    </section>
  );
}
