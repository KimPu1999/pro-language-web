"use client";

import { useState } from "react";

export function PhpPlayground({ code, title = "PHP practice" }: { code: string; title?: string }) {
  const [status, setStatus] = useState("");

  async function copy() {
    try { await navigator.clipboard.writeText(code); setStatus("PHP copied."); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([code], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "codemaster-practice.php"; anchor.click(); URL.revokeObjectURL(url);
    setStatus("PHP file downloaded.");
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-indigo-400/20 bg-surface" aria-labelledby="php-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-300">Safe PHP code viewer</p>
        <h2 id="php-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">This read-only viewer keeps arbitrary PHP outside the application server. A strongly isolated PHP runner is required before hosted execution is enabled.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-[1fr_18rem]">
        <div>
          <pre className="min-h-[300px] overflow-auto bg-[#0d1528] p-5 text-sm leading-7 text-slate-200" tabIndex={0} aria-label="PHP source"><code>{code}</code></pre>
          <div className="flex flex-wrap items-center gap-2 border-t border-line p-4">
            <button type="button" onClick={copy} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy code</button>
            <button type="button" onClick={download} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download .php</button>
            {status && <span className="text-xs text-emerald-300" role="status">{status}</span>}
          </div>
        </div>
        <aside className="border-t border-line p-5 lg:border-l lg:border-t-0" aria-label="PHP local run instructions">
          <h3 className="font-semibold text-indigo-100">Run locally</h3>
          <code className="mt-3 block whitespace-pre-wrap rounded-lg bg-black/30 p-3 text-xs leading-6 text-emerald-200">php --version{`\n`}php -l index.php{`\n`}php index.php</code>
          <p className="mt-4 text-xs leading-5 text-slate-500">Review the source first. Never place secrets in PHP examples or execute untrusted PHP inside FastAPI workers. Use a dedicated isolated environment for experiments.</p>
        </aside>
      </div>
    </section>
  );
}
