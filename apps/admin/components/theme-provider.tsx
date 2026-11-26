"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { LanguageSwitcher } from "@/components/language-switcher";

export type ThemeMode = "light" | "dark" | "system";
type ThemeContextValue = { theme: ThemeMode; resolvedTheme: "light" | "dark"; setTheme: (theme: ThemeMode) => void };
const ThemeContext = createContext<ThemeContextValue | null>(null);

function applyTheme(theme: ThemeMode, systemDark = false) {
  const resolved = theme === "system" ? (systemDark ? "dark" : "light") : theme;
  document.documentElement.classList.toggle("dark", resolved === "dark");
  document.documentElement.dataset.theme = resolved;
  document.documentElement.style.colorScheme = resolved;
  return resolved;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>("system");
  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">("light");
  useEffect(() => { const stored = window.localStorage.getItem("learn-coding-theme") as ThemeMode | null; if (stored === "light" || stored === "dark" || stored === "system") setThemeState(stored); }, []);
  useEffect(() => { const media = window.matchMedia("(prefers-color-scheme: dark)"), sync = () => setResolvedTheme(applyTheme(theme, media.matches) as "light" | "dark"); sync(); const onSystemChange = () => { if (theme === "system") sync(); }; media.addEventListener?.("change", onSystemChange); return () => media.removeEventListener?.("change", onSystemChange); }, [theme]);
  function setTheme(next: ThemeMode) { window.localStorage.setItem("learn-coding-theme", next); setThemeState(next); }
  const value = useMemo(() => ({ theme, resolvedTheme, setTheme }), [theme, resolvedTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() { const value = useContext(ThemeContext); if (!value) throw new Error("useTheme must be used inside ThemeProvider"); return value; }
export function ThemeSwitcher({ className = "" }: { className?: string }) { const { theme, setTheme } = useTheme(); const [open, setOpen] = useState(false); const options = [{ value: "light" as const, label: "Light", icon: Sun }, { value: "dark" as const, label: "Dark", icon: Moon }, { value: "system" as const, label: "System", icon: Monitor }]; const selected = options.find(option => option.value === theme) ?? options[2]; const SelectedIcon = selected.icon; return <div className={`relative flex items-center gap-2 ${className}`}><LanguageSwitcher /><button type="button" aria-label={`Theme: ${selected.label}`} aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(value => !value)} className="flex h-10 items-center gap-2 rounded-xl border border-line bg-surface px-3 text-xs text-muted transition hover:bg-surface-hover hover:text-foreground"><SelectedIcon size={16} /><span className="hidden sm:inline">{selected.label}</span></button>{open && <div role="menu" aria-label="Theme preference" className="absolute right-0 top-12 z-50 w-36 rounded-xl border border-line bg-surface p-1.5 shadow-panel">{options.map(option => { const Icon = option.icon; return <button key={option.value} type="button" role="menuitemradio" aria-checked={theme === option.value} onClick={() => { setTheme(option.value); setOpen(false); }} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition ${theme === option.value ? "bg-primary/12 text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}><Icon size={15} />{option.label}</button>; })}</div>}</div>; }
