"use client";

import { useState } from "react";

type Props = { code: string; title?: string };

export function JqueryPlayground({ code, title = "jQuery practice" }: Props) {
  const [status, setStatus] = useState("");
  const html = "<main id=\"demo\" aria-live=\"polite\">\n  <h1>jQuery practice</h1>\n  <button id=\"save\" type=\"button\">Save</button>\n</main>";
  const css = "body { font-family: system-ui, sans-serif; padding: 1rem; }\nbutton { padding: .5rem .75rem; }";

  async function copy(value: string, label: string) {
    try { await navigator.clipboard.writeText(value); setStatus(`${label} copied.`); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download(filename: string, value: string) {
    const url = URL.createObjectURL(new Blob([value], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click(); URL.revokeObjectURL(url);
    setStatus(`${filename} downloaded.`);
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-sky-400/20 bg-surface" aria-labelledby="jquery-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-300">Safe jQuery practice</p>
        <h2 id="jquery-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">This read-only project viewer keeps student code outside the parent application. A verified sandbox and pinned jQuery build are required before live execution is enabled.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-3">
        {[
          ["index.html", html],
          ["styles.css", css],
          ["app.js", code],
        ].map(([filename, value]) => (
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
          <li>Download the three files and add a reviewed, pinned jQuery 4.x build locally.</li>
          <li>Use a CSP and an isolated test page; never grant parent-page access to untrusted code.</li>
          <li>For jQuery 3.x maintenance, run the migration checks before shipping changes.</li>
        </ol>
        {status && <p className="mt-3 text-emerald-300" role="status">{status}</p>}
      </div>
    </section>
  );
}
