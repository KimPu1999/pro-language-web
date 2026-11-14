"use client";

import { useState } from "react";

export function CsharpPlayground({ code, title = "C# practice" }: { code: string; title?: string }) {
  const [status, setStatus] = useState("");

  async function copy() {
    try { await navigator.clipboard.writeText(code); setStatus("C# copied."); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([code], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "Program.cs"; anchor.click(); URL.revokeObjectURL(url);
    setStatus("Program.cs downloaded.");
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-purple-400/20 bg-surface" aria-labelledby="csharp-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-purple-300">Safe C# code viewer</p>
        <h2 id="csharp-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">This read-only viewer keeps arbitrary .NET code outside the application server. A strongly isolated .NET runner is required before hosted compilation or execution is enabled.</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-[1fr_18rem]">
        <div>
          <pre className="min-h-[300px] overflow-auto bg-[#0d1528] p-5 text-sm leading-7 text-slate-200" tabIndex={0} aria-label="C# source"><code>{code}</code></pre>
          <div className="flex flex-wrap items-center gap-2 border-t border-line p-4">
            <button type="button" onClick={copy} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy code</button>
            <button type="button" onClick={download} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download .cs</button>
            {status && <span className="text-xs text-emerald-300" role="status">{status}</span>}
          </div>
        </div>
        <aside className="border-t border-line p-5 lg:border-l lg:border-t-0" aria-label=".NET local run instructions">
          <h3 className="font-semibold text-purple-100">Run locally</h3>
          <code className="mt-3 block whitespace-pre-wrap rounded-lg bg-black/30 p-3 text-xs leading-6 text-emerald-200">dotnet --version{`\n`}dotnet new console{`\n`}dotnet build{`\n`}dotnet run</code>
          <p className="mt-4 text-xs leading-5 text-slate-500">Use the project’s documented SDK and target framework. Never run untrusted C# inside FastAPI workers or expose secrets in examples.</p>
        </aside>
      </div>
    </section>
  );
}
