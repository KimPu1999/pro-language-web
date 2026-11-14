"use client";

import { useMemo, useRef, useState } from "react";

type Example = { title: string; html: string; css: string };

function previewDocument(html: string, css: string) {
  const policy = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; img-src data:;\">";
  const style = `<style>${css}</style>`;
  if (/<head[\s>]/i.test(html)) return html.replace(/<head([^>]*)>/i, `<head$1>${policy}${style}`);
  return `<!doctype html><html lang="en"><head>${policy}${style}</head><body>${html}</body></html>`;
}

export function CssPlayground({ examples, title = "CSS playground" }: { examples: Example[]; title?: string }) {
  const [selected, setSelected] = useState(0);
  const [html, setHtml] = useState(examples[0]?.html ?? "<main class=\"card\"><h1>Hello CSS</h1><p>Edit the stylesheet.</p></main>");
  const [css, setCss] = useState(examples[0]?.css ?? ".card { color: #264de4; padding: 2rem; }");
  const [viewport, setViewport] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [status, setStatus] = useState("");
  const previewRef = useRef<HTMLIFrameElement>(null);
  const cssError = useMemo(() => {
    const opens = (css.match(/{/g) ?? []).length;
    const closes = (css.match(/}/g) ?? []).length;
    return opens === closes ? "" : "CSS feedback: check the number of opening and closing braces.";
  }, [css]);

  function chooseExample(index: number) {
    const example = examples[index];
    setSelected(index);
    setHtml(example?.html ?? "");
    setCss(example?.css ?? "");
    setStatus("");
  }

  function reset() {
    chooseExample(selected);
    setStatus("Example reset.");
  }

  async function copy(value: string, label: string) {
    try { await navigator.clipboard.writeText(value); setStatus(`${label} copied.`); }
    catch { setStatus("Copy is unavailable in this browser."); }
  }

  function download() {
    const documentSource = previewDocument(html, css);
    const url = URL.createObjectURL(new Blob([documentSource], { type: "text/html;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "codemaster-css-practice.html"; anchor.click(); URL.revokeObjectURL(url);
    setStatus("HTML file with embedded CSS downloaded.");
  }

  async function fullscreen() {
    try { await previewRef.current?.requestFullscreen(); }
    catch { setStatus("Fullscreen is unavailable in this browser."); }
  }

  const width = viewport === "mobile" ? "max-w-[390px]" : viewport === "tablet" ? "max-w-[768px]" : "w-full";
  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-blue-400/20 bg-surface" aria-labelledby="css-playground-title">
      <div className="border-b border-line p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-300">Safe CSS practice</p>
            <h2 id="css-playground-title" className="mt-1 text-xl font-bold">{title}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Edit HTML and CSS, then compare desktop, tablet, and mobile layouts in an isolated preview. Scripts and parent-page access are disabled.</p>
          </div>
          <div className="flex flex-wrap gap-2" role="tablist" aria-label="CSS examples">
            {examples.map((example, index) => <button key={`${example.title}-${index}`} type="button" role="tab" aria-selected={selected === index} onClick={() => chooseExample(index)} className={`rounded-lg px-3 py-2 text-xs ${selected === index ? "bg-blue-500/20 text-blue-200" : "bg-ink text-slate-400"}`}>Example {index + 1}</button>)}
          </div>
        </div>
      </div>
      <div className="grid gap-0 xl:grid-cols-[1fr_1fr_1.1fr]">
        <div className="border-b border-line xl:border-b-0 xl:border-r">
          <label htmlFor="css-html-editor" className="block border-b border-line px-4 py-3 text-xs font-semibold text-slate-400">HTML</label>
          <textarea id="css-html-editor" value={html} onChange={event => setHtml(event.target.value)} spellCheck={false} className="min-h-[240px] w-full resize-y bg-[#0d1528] p-4 font-mono text-sm leading-6 text-slate-200 outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-400" />
          <button type="button" onClick={() => copy(html, "HTML")} className="m-3 rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy HTML</button>
        </div>
        <div className="border-b border-line xl:border-b-0 xl:border-r">
          <label htmlFor="css-style-editor" className="block border-b border-line px-4 py-3 text-xs font-semibold text-slate-400">CSS</label>
          <textarea id="css-style-editor" value={css} onChange={event => setCss(event.target.value)} spellCheck={false} className="min-h-[240px] w-full resize-y bg-[#0d1528] p-4 font-mono text-sm leading-6 text-slate-200 outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-400" />
          <button type="button" onClick={() => copy(css, "CSS")} className="m-3 rounded-lg border border-line px-3 py-2 text-xs text-slate-300">Copy CSS</button>
        </div>
        <div className="min-w-0 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 px-3 py-3 text-xs text-slate-600">
            <div className="flex gap-1" role="group" aria-label="Preview viewport">
              {(["desktop", "tablet", "mobile"] as const).map(item => <button key={item} type="button" onClick={() => setViewport(item)} className={`rounded px-2 py-1 capitalize ${viewport === item ? "bg-blue-100 text-blue-800" : "text-slate-500"}`}>{item}</button>)}
            </div>
            <button type="button" onClick={fullscreen} className="rounded border border-slate-300 px-2 py-1 text-slate-700">Fullscreen</button>
          </div>
          <div className="flex min-h-[330px] justify-center bg-slate-100 p-2">
            <iframe ref={previewRef} title="Sandboxed HTML and CSS browser preview" srcDoc={previewDocument(html, css)} sandbox="" referrerPolicy="no-referrer" onLoad={() => setStatus("Preview updated.")} className={`h-[330px] w-full border-0 bg-white ${width}`} />
          </div>
          <div className="flex flex-wrap items-center gap-2 border-t border-slate-200 p-3">
            <button type="button" onClick={reset} className="rounded border border-slate-300 px-3 py-2 text-xs text-slate-700">Reset</button>
            <button type="button" onClick={download} className="rounded border border-slate-300 px-3 py-2 text-xs text-slate-700">Download</button>
            {(cssError || status) && <span className={`text-xs ${cssError ? "text-rose-700" : "text-emerald-700"}`} role="status">{cssError || status}</span>}
          </div>
        </div>
      </div>
      <p className="border-t border-line px-5 py-3 text-xs leading-5 text-slate-500">Security boundary: the iframe has an empty sandbox and a restrictive preview CSP. Student CSS cannot style the parent page.</p>
    </section>
  );
}
