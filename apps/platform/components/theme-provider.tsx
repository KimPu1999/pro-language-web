"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

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

  useEffect(() => {
    const stored = window.localStorage.getItem("learn-coding-theme") as ThemeMode | null;
    if (stored === "light" || stored === "dark" || stored === "system") setThemeState(stored);
  }, []);
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const sync = () => setResolvedTheme(applyTheme(theme, media.matches) as "light" | "dark");
    sync();
    const onSystemChange = () => { if (theme === "system") sync(); };
    media.addEventListener?.("change", onSystemChange);
    return () => media.removeEventListener?.("change", onSystemChange);
  }, [theme]);

  function setTheme(next: ThemeMode) {
    window.localStorage.setItem("learn-coding-theme", next);
    setThemeState(next);
  }

  const value = useMemo(() => ({ theme, resolvedTheme, setTheme }), [theme, resolvedTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) throw new Error("useTheme must be used inside ThemeProvider");
  return value;
}

export function ThemeSwitcher({ className = "" }: { className?: string }) {
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const Icon = theme === "light" ? Sun : theme === "dark" ? Moon : Monitor;
  const label = theme === "system" ? "System theme" : theme === "light" ? "Light theme" : "Dark theme";
  const options: { value: ThemeMode; label: string; icon: typeof Sun }[] = [{ value: "light", label: "Light", icon: Sun }, { value: "dark", label: "Dark", icon: Moon }, { value: "system", label: "System", icon: Monitor }];
  return <div className={`relative ${className}`}>
    <button type="button" aria-label={label} aria-expanded={open} aria-haspopup="menu" onClick={() => setOpen(value => !value)} className="grid h-9 w-9 place-items-center rounded-lg border border-line bg-surface text-muted transition hover:bg-surface-hover hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40">
      <Icon size={17} aria-hidden="true" />
    </button>
    {open && <div role="menu" aria-label="Theme preference" className="absolute right-0 top-11 z-50 min-w-36 rounded-xl border border-line bg-surface p-1.5 shadow-lg">
      {options.map(option => { const OptionIcon = option.icon; return <button key={option.value} type="button" role="menuitemradio" aria-checked={theme === option.value} onClick={() => { setTheme(option.value); setOpen(false); }} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition ${theme === option.value ? "bg-primary/15 text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}><OptionIcon size={15} aria-hidden="true" /> {option.label}</button>; })}
    </div>}
  </div>;
}
