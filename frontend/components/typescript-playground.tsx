"use client";

import { useState } from "react";

export function TypescriptPlayground({ code, title = "TypeScript practice" }: { code: string; title?: string }) {
  const [status, setStatus] = useState("");

  async function copy() {
    try { await navigator.clipboard.writeText(code); setStatus("TypeScript copied."); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([code], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "codemaster-practice.ts"; anchor.click(); URL.revokeObjectURL(url);
    setStatus("TypeScript file downloaded.");
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-blue-400/20 bg-surface" aria-labelledby="typescript-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-300">TypeScript code viewer</p>
        <h2 id="typescript-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">This safe viewer preserves the source and explains the real compiler workflow. A full TypeScript language service and isolated runtime are not enabled in this deployment, so diagnostics and execution are not simulated.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-[1fr_18rem]">
        <div>
          <pre className="min-h-[300px] overflow-auto bg-[#0d1528] p-5 text-sm leading-7 text-slate-200" tabIndex={0} aria-label="TypeScript source"><code>{code}</code></pre>
          <div className="flex flex-wrap items-center gap-2 border-t border-line p-4">
            <button type="button" onClick={copy} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy code</button>
            <button type="button" onClick={download} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download .ts</button>
            {status && <span className="text-xs text-emerald-300" role="status">{status}</span>}
          </div>
        </div>
        <aside className="border-t border-line p-5 lg:border-l lg:border-t-0" aria-label="TypeScript compiler instructions">
          <h3 className="font-semibold text-blue-100">Check locally</h3>
          <code className="mt-3 block whitespace-pre-wrap rounded-lg bg-black/30 p-3 text-xs leading-6 text-emerald-200">npm install --save-dev typescript{`\n`}npx tsc --noEmit{`\n`}npx tsc{`\n`}node dist/main.js</code>
          <p className="mt-4 text-xs leading-5 text-slate-500">`tsc --noEmit` performs type checking. Transpiling alone is not full type checking. Do not run untrusted code inside the application server.</p>
        </aside>
      </div>
    </section>
  );
}
