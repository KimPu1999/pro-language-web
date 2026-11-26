"use client";
import { Languages } from "lucide-react";
import { useI18n, type Locale } from "@/lib/i18n";
export function LanguageSwitcher() { const { locale, setLocale, t } = useI18n(); const button = (next: Locale, label: string) => <button type="button" aria-pressed={locale === next} onClick={() => setLocale(next)} className={`rounded px-1.5 py-0.5 font-semibold ${locale === next ? "bg-primary/20 text-primary" : "text-muted hover:text-foreground"}`}>{label}</button>; return <div className="inline-flex items-center gap-1 rounded-lg border border-line bg-surface/60 px-1.5 py-1 text-xs" aria-label={t("language")}><Languages size={14} className="mx-1 text-muted" aria-hidden="true" />{button("en", "EN")}<span className="text-muted">|</span>{button("my", "MM")}</div>; }
