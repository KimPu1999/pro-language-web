"use client";

import Link from "next/link";
import { RefreshCw, Terminal } from "lucide-react";
import { useState } from "react";
import { useI18n } from "@/lib/i18n";

const examples = [{ name: "Route example", code: "Route::get('/profile', function () {\n    return view('profile');\n});", output: "GET /profile -> Blade view profile (simulated)" }, { name: "Validation example", code: "$validated = $request->validate([\n    'name' => ['required', 'string', 'max:120'],\n]);", output: "Validated request data (simulated)" }, { name: "Artisan example", code: "php artisan make:controller ProfileController\nphp artisan route:list", output: "Controller created; routes listed (simulated)" }];

export default function LaravelPlaygroundPage() {
  const [selected, setSelected] = useState(0);
  const [output, setOutput] = useState("Select a supported example to inspect its expected result.");
  const example = examples[selected];
  const { locale } = useI18n();
  const safetyNote = locale === "my"
    ? "ဥပမာများကို ကြိုတင်သတ်မှတ်ထားပြီး browser ထဲတွင်သာ ပြသထားပါသည်။ PHP runtime၊ shell၊ database၊ filesystem သို့မဟုတ် မယုံကြည်ရသော code များကို execute လုပ်နိုင်သည့် စနစ်မရှိပါ။"
    : "Examples are predefined and rendered in the browser. No PHP runtime, shell, database, filesystem, or untrusted code execution is available.";
  return <section className="mx-auto max-w-6xl px-5 py-12 lg:px-8"><Link href="/courses/laravel" className="text-sm text-red-300 hover:text-white">← Back to Laravel course</Link><div className="mt-8 max-w-3xl"><p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">Laravel playground</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">Safe PHP and Artisan examples</h1><p className="mt-4 text-lg leading-8 text-slate-400">Inspect predefined Laravel examples and simulated results. This page does not execute PHP or Artisan.</p></div><div className="mt-10 grid gap-6 lg:grid-cols-[.75fr_1.25fr]"><div className="rounded-2xl border border-line bg-surface p-5"><div className="flex items-center gap-3 text-red-300"><Terminal size={20}/><h2 className="font-semibold">Examples</h2></div><div className="mt-4 space-y-2">{examples.map((item, index) => <button key={item.name} onClick={() => { setSelected(index); setOutput(item.output); }} className={"block w-full rounded-lg px-3 py-2 text-left text-sm " + (index === selected ? "bg-red-500/15 text-red-100" : "bg-ink text-slate-300 hover:bg-white/5")}>{item.name}</button>)}</div><button onClick={() => { setSelected(0); setOutput("Select a supported example to inspect its expected result."); }} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm text-slate-300"><RefreshCw size={15}/> Reset</button></div><div className="space-y-5"><div className="rounded-2xl border border-red-400/20 bg-[#0a1220] p-5"><p className="text-xs uppercase tracking-wider text-red-300">PHP / Artisan example</p><pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-red-100"><code>{example.code}</code></pre></div><div className="rounded-2xl border border-line bg-surface p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Simulated result</p><pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-200"><code>{output}</code></pre></div></div></div><p className="mt-6 rounded-xl bg-amber-400/10 p-4 text-xs leading-5 text-amber-200">{safetyNote}</p></section>;
}
