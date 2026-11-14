"use client";

import { useState } from "react";

export function JavaPlayground({ code, title = "Java practice" }: { code: string; title?: string }) {
  const [status, setStatus] = useState("");
  async function copy() {
    try { await navigator.clipboard.writeText(code); setStatus("Java copied."); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([code], { type: "text/x-java-source;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "codemaster-Main.java"; anchor.click(); URL.revokeObjectURL(url); setStatus("Main.java downloaded.");
  }
  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-orange-400/20 bg-surface" aria-labelledby="java-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-orange-300">Safe Java practice</p>
        <h2 id="java-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">This is a protected read-only viewer. The platform does not compile or execute arbitrary Java in the browser, FastAPI worker, or application host. Examples target Java 25 LTS; copy them to a trusted local JDK environment.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-[1fr_18rem]">
        <div>
          <pre className="min-h-[340px] overflow-auto bg-[#0d1528] p-5 text-sm leading-7 text-slate-200" tabIndex={0} aria-label="Java source"><code>{code}</code></pre>
          <div className="flex flex-wrap items-center gap-2 border-t border-line p-4">
            <button type="button" onClick={copy} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy code</button>
            <button type="button" onClick={download} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download .java</button>
            {status && <span className="text-xs text-emerald-300" role="status">{status}</span>}
          </div>
        </div>
        <aside className="border-t border-line p-5 lg:border-l lg:border-t-0" aria-label="Local Java run instructions">
          <h3 className="font-semibold text-orange-100">Run locally with Java 25</h3>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6 text-slate-400">
            <li>Save the file as <code>Main.java</code> when it contains <code>public class Main</code>.</li>
            <li>Check <code>java --version</code> and <code>javac --version</code>.</li>
            <li>Compile with <code>javac Main.java</code>.</li>
            <li>Run with <code>java Main</code>.</li>
          </ol>
          <p className="mt-4 text-xs leading-5 text-slate-500">Execution is intentionally unavailable until a separately audited sandbox service is configured with process, CPU, memory, filesystem, network, output, and concurrency limits.</p>
        </aside>
      </div>
    </section>
  );
}
