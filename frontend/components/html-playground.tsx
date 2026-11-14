"use client";

import { useRef, useState } from "react";

type Example = { title: string; code: string };

export function HtmlPlayground({ examples, title = "HTML playground" }: { examples: Example[]; title?: string }) {
  const [selected, setSelected] = useState(0);
  const [code, setCode] = useState(examples[0]?.code ?? "<!doctype html>\n<html lang=\"en\">\n  <body>\n    <h1>Hello, HTML!</h1>\n  </body>\n</html>");
  const [status, setStatus] = useState("");
  const previewRef = useRef<HTMLIFrameElement>(null);

  function chooseExample(index: number) {
    setSelected(index);
    setCode(examples[index]?.code ?? "");
    setStatus("");
  }

  function reset() {
    setCode(examples[selected]?.code ?? "");
    setStatus("Example reset.");
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setStatus("HTML copied.");
    } catch {
      setStatus("Copy is unavailable in this browser.");
    }
  }

  function download() {
    const blob = new Blob([code], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "codemaster-html-practice.html";
    anchor.click();
    URL.revokeObjectURL(url);
    setStatus("HTML file downloaded.");
  }

  async function fullscreen() {
    try {
      await previewRef.current?.requestFullscreen();
    } catch {
      setStatus("Fullscreen is unavailable in this browser.");
    }
  }

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-orange-400/20 bg-surface" aria-labelledby="html-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-orange-300">Safe HTML practice</p>
            <h2 id="html-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Edit the markup and preview it in an isolated iframe. Scripts, forms, popups, and parent-page access are disabled.</p>
          </div>
          <div className="flex flex-wrap gap-2" role="tablist" aria-label="HTML examples">
            {examples.map((example, index) => (
              <button key={`${example.title}-${index}`} type="button" role="tab" aria-selected={selected === index} onClick={() => chooseExample(index)} className={`rounded-lg px-3 py-2 text-xs ${selected === index ? "bg-orange-500/20 text-orange-200" : "bg-ink text-slate-400"}`}>
                Example {index + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="grid gap-0 lg:grid-cols-2">
        <div className="border-b border-line lg:border-b-0 lg:border-r">
          <label htmlFor="html-playground-editor" className="sr-only">HTML source editor</label>
          <textarea id="html-playground-editor" value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} className="min-h-[330px] w-full resize-y bg-[#0d1528] p-5 font-mono text-sm leading-6 text-slate-200 outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-400" aria-describedby="html-playground-security" />
          <div className="flex flex-wrap items-center gap-2 border-t border-line p-4">
            <button type="button" onClick={reset} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Reset</button>
            <button type="button" onClick={copy} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy HTML</button>
            <button type="button" onClick={download} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Download</button>
            {status && <span className="text-xs text-emerald-300" role="status">{status}</span>}
          </div>
        </div>
        <div className="min-w-0 bg-white">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 text-xs text-slate-600">
            <span>Browser preview</span>
            <button type="button" onClick={fullscreen} className="rounded border border-slate-300 px-2 py-1 text-slate-700">Fullscreen</button>
          </div>
          <iframe ref={previewRef} title="Sandboxed HTML browser preview" srcDoc={code} sandbox="" referrerPolicy="no-referrer" className="h-[330px] w-full border-0" />
        </div>
      </div>
      <p id="html-playground-security" className="border-t border-line px-5 py-3 text-xs leading-5 text-slate-500">Security boundary: this preview uses an empty sandbox, so the authored document cannot run scripts or access the parent application.</p>
    </section>
  );
}
