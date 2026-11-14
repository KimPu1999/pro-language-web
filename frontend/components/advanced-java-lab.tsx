"use client";

import { useState } from "react";

type EnterpriseFile = { filename: string; code: string; language: string };

export function AdvancedJavaLab({ files }: { files: EnterpriseFile[] }) {
  const [selected, setSelected] = useState(0);
  const current = files[selected];

  if (!current) return null;

  async function copy() {
    await navigator.clipboard.writeText(current.code);
  }

  function download() {
    const blob = new Blob([current.code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = current.filename || "Main.java";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="mt-10 overflow-hidden rounded-2xl border border-line bg-[#0b1020]" aria-label="Enterprise Java code lab">
      <div className="border-b border-line bg-surface/80 p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-orange-300">Enterprise code lab</p>
            <h2 className="mt-2 text-xl font-bold">Project files and local setup</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Inspect Java, build, configuration, SQL, and test files together. Hosted arbitrary Java execution is disabled until an isolated runner is configured and verified.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={copy} className="rounded-lg border border-line px-3 py-2 text-sm text-slate-200 hover:border-indigo-400">Copy file</button>
            <button onClick={download} className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500">Download file</button>
          </div>
        </div>
      </div>
      <div className="grid md:grid-cols-[210px_1fr]">
        <nav className="border-b border-line p-3 md:border-b-0 md:border-r" aria-label="Project files">
          <p className="px-2 pb-2 text-xs uppercase tracking-wide text-slate-500">Files</p>
          <div className="space-y-1">
            {files.map((file, index) => (
              <button key={`${file.filename}-${index}`} onClick={() => setSelected(index)} className={`w-full rounded-lg px-3 py-2 text-left text-sm ${index === selected ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:bg-white/5"}`} aria-current={index === selected ? "page" : undefined}>
                {file.filename}
              </button>
            ))}
          </div>
        </nav>
        <div className="min-w-0">
          <div className="flex items-center justify-between border-b border-line px-4 py-3 text-xs text-slate-500"><span>{current.filename}</span><span>{current.language}</span></div>
          <pre className="max-h-[520px] overflow-auto p-4 text-sm leading-6 text-indigo-100"><code>{current.code}</code></pre>
          <div className="border-t border-line p-4 text-sm leading-6 text-slate-400">
            <p className="font-medium text-slate-200">Local run instructions</p>
            <code className="mt-2 block whitespace-pre-wrap rounded-lg bg-black/30 p-3 text-xs text-emerald-200">java --version{`\n`}javac --release 25 {current.filename || "Main.java"}{`\n`}java Main</code>
            <p className="mt-3">Use a local JDK or an approved isolated runner. Do not paste secrets into examples or run untrusted code inside the API process.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
