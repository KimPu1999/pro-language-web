"use client";

import { Languages } from "lucide-react";
import { useI18n, type Locale } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();
  const choose = (next: Locale) => { if (next !== locale) setLocale(next); };
  return <div className="inline-flex items-center gap-1 rounded-lg border border-line/80 bg-surface/50 px-1.5 py-1 text-xs" aria-label={t("language")}>
    <Languages size={14} className="mx-1 text-slate-400" aria-hidden="true" />
    <button type="button" aria-pressed={locale === "en"} onClick={() => choose("en")} className={`rounded px-1.5 py-0.5 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${locale === "en" ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:text-white"}`}>EN</button>
    <span className="text-slate-600">|</span>
    <button type="button" aria-pressed={locale === "my"} onClick={() => choose("my")} className={`rounded px-1.5 py-0.5 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${locale === "my" ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:text-white"}`}>MM</button>
  </div>;
}
