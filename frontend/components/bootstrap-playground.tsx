"use client";

import { useState } from "react";

export function BootstrapPlayground({ code, title = "Bootstrap practice" }: { code: string; title?: string }) {
  const [status, setStatus] = useState("");
  const files = [
    ["index.html", code],
    ["styles.css", ":root { --bs-primary: #7952b3; }\n/* Add focused project overrides here. */"],
    ["app.js", "// Bootstrap 5.3.x plugins use vanilla JavaScript.\n// Add behavior only after the isolated preview is verified."],
  ] as const;

  async function copy(value: string, filename: string) {
    try { await navigator.clipboard.writeText(value); setStatus(`${filename} copied.`); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download(filename: string, value: string) {
    const url = URL.createObjectURL(new Blob([value], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click(); URL.revokeObjectURL(url);
    setStatus(`${filename} downloaded.`);
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-violet-400/20 bg-surface" aria-labelledby="bootstrap-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-violet-300">Safe Bootstrap practice</p>
        <h2 id="bootstrap-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">Inspect the HTML, CSS, and JavaScript project files. A verified sandbox and pinned Bootstrap 5.3.x assets are required before live execution is enabled.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-3">
        {files.map(([filename, value]) => (
          <div key={filename} className="min-w-0 border-b border-line lg:border-b-0 lg:border-r last:lg:border-r-0">
            <div className="flex items-center justify-between border-b border-line px-4 py-3 text-xs text-slate-400"><span>{filename}</span><button type="button" onClick={() => copy(value, filename)} className="rounded border border-line px-2 py-1 hover:border-indigo-400">Copy</button></div>
            <pre className="min-h-[230px] overflow-auto bg-[#0d1528] p-4 text-xs leading-6 text-slate-200"><code>{value}</code></pre>
            <div className="border-t border-line p-3"><button type="button" onClick={() => download(filename, value)} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download {filename}</button></div>
          </div>
        ))}
      </div>
      <div className="border-t border-line p-5 text-sm leading-6 text-slate-400">
        <p className="font-semibold text-slate-200">Local preview instructions</p>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          <li>Use the exact reviewed Bootstrap 5.3.x CSS and matching bundle version.</li>
          <li>Preview in an isolated sandbox with a restrictive CSP; do not grant parent-page access.</li>
          <li>Test mobile, tablet, desktop, keyboard focus, reduced motion, and long content.</li>
        </ol>
        {status && <p className="mt-3 text-emerald-300" role="status">{status}</p>}
      </div>
    </section>
  );
}
