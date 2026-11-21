"use client";

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
  return <label className={`flex items-center gap-2 text-xs text-muted ${className}`}><span className="sr-only">Theme</span><select aria-label="Theme preference" value={theme} onChange={event => setTheme(event.target.value as ThemeMode)} className="h-9 rounded-lg border border-line bg-surface px-2 text-xs text-foreground outline-none transition focus:border-primary"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>;
}
