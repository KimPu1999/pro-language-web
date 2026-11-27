"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { ArrowRight, BookOpen, Clock, Eye, EyeOff, FileText, LayoutDashboard, ListChecks, Menu, Search, Sparkles, Tags, X } from "lucide-react";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { api, coursesApi } from "@/lib/api";
import type { Course } from "@/lib/types";
import { LogoutButton } from "@/components/auth-form";
import { useI18n } from "@/lib/i18n";

type DashboardLanguage = "en" | "my";
type DashboardPreferences = { language: DashboardLanguage; theme: "dark" | "light"; setLanguage: (value: DashboardLanguage) => void; toggleTheme: () => void };
const PreferencesContext = createContext<DashboardPreferences | null>(null);
export function useDashboardPreferences() { return useContext(PreferencesContext) ?? { language: "en" as const, theme: "dark" as const, setLanguage: () => undefined, toggleTheme: () => undefined }; }
const copy = { en: { overview: "Overview", courses: "My courses", notebook: "My notebook", analytics: "Learning analytics", quizzes: "Quizzes", projects: "Projects", certificates: "Certificates", achievements: "Achievements", planner: "Study planner", notifications: "Notifications", profile: "My profile", settings: "Settings", main: "Main", tools: "Learning tools", community: "Community", account: "Account", momentum: "Keep your momentum", browse: "Browse courses", search: "Search courses and lessons…", profileMenu: "Profile menu", theme: "Toggle theme", language: "Switch to Myanmar" }, my: { overview: "အနှစ်ချုပ်", courses: "ကျွန်ုပ်၏သင်တန်းများ", notebook: "မှတ်စုစာအုပ်", analytics: "လေ့လာမှုခွဲခြမ်းစိတ်ဖြာမှု", quizzes: "ဉာဏ်စမ်းများ", projects: "ပရောဂျက်များ", certificates: "လက်မှတ်များ", achievements: "အောင်မြင်မှုများ", planner: "လေ့လာမှုအစီအစဉ်", notifications: "အသိပေးချက်များ", profile: "ကိုယ်ရေးအချက်အလက်", settings: "ဆက်တင်များ", main: "အဓိက", tools: "လေ့လာရေးကိရိယာများ", community: "အသိုင်းအဝိုင်း", account: "အကောင့်", momentum: "ဆက်လက်ကြိုးစားပါ", browse: "သင်တန်းများကြည့်ရန်", search: "သင်တန်းနှင့် သင်ခန်းစာရှာရန်…", profileMenu: "ကိုယ်ရေးမီနူး", theme: "အပြင်အဆင်ပြောင်းရန်", language: "အင်္ဂလိပ်သို့ပြောင်းရန်" } } as const;

const items = [
  ["Overview", "/dashboard", LayoutDashboard], ["My courses", "/dashboard/courses", BookOpen], ["My notebook", "/dashboard/notebook", FileText], ["Learning analytics", "/dashboard/analytics", Sparkles],
  ["Quizzes", "/dashboard/assessments", ListChecks], ["Projects", "/my-projects", BookOpen], ["Certificates", "/dashboard/certificates", Sparkles],
  ["Achievements", "/dashboard/achievements", Sparkles], ["Study planner", "/dashboard/study-plan", Clock], ["Notifications", "/settings/notifications", Sparkles],
  ["Profile", "/profile", Eye], ["Settings", "/settings", Tags],
] as const;

export function StudentDashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { locale: language, setLocale } = useI18n();
  const [collapsed, setCollapsed] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Course[]>([]);
  const [searching, setSearching] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLElement>(null);
  useEffect(() => setCollapsed(window.localStorage.getItem("cm_dashboard_sidebar") === "collapsed"), []);
  useEffect(() => { const savedTheme = window.localStorage.getItem("cm_theme"); if (savedTheme === "light") { setTheme("light"); document.documentElement.classList.add("theme-light"); } }, []);
  useEffect(() => { if (!drawer) return; const previous = document.activeElement as HTMLElement | null; document.body.style.overflow = "hidden"; drawerRef.current?.querySelector<HTMLElement>("a,button")?.focus(); const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") { setDrawer(false); menuButtonRef.current?.focus(); return; } if (event.key !== "Tab" || !drawerRef.current) return; const focusable = Array.from(drawerRef.current.querySelectorAll<HTMLElement>("a,button")); const first = focusable[0]; const last = focusable[focusable.length - 1]; if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); } else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); } }; document.addEventListener("keydown", onKeyDown); return () => { document.body.style.overflow = ""; document.removeEventListener("keydown", onKeyDown); previous?.focus(); }; }, [drawer]);
  useEffect(() => {
    if (query.trim().length < 2) { setResults([]); setSearching(false); return; }
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setSearching(true);
      coursesApi(`?search=${encodeURIComponent(query.trim())}&page_size=5`, controller.signal)
        .then(data => setResults(data.items))
        .catch(reason => { if (reason instanceof Error && reason.name === "AbortError") return; setResults([]); })
        .finally(() => { if (!controller.signal.aborted) setSearching(false); });
    }, 250);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query]);
  const toggle = () => setCollapsed(value => { const next = !value; window.localStorage.setItem("cm_dashboard_sidebar", next ? "collapsed" : "expanded"); return next; });
  const text = copy[language];
  const changeLanguage = (value: DashboardLanguage) => { setLocale(value); window.dispatchEvent(new CustomEvent("cm-language-change", { detail: value })); };
  const toggleTheme = () => { const next = theme === "dark" ? "light" : "dark"; setTheme(next); window.localStorage.setItem("cm_theme", next); document.documentElement.classList.toggle("theme-light", next === "light"); };
  const navLabels = [text.overview, text.courses, text.notebook, text.analytics, text.quizzes, text.projects, text.certificates, text.achievements, text.planner, text.notifications, text.profile, text.settings];
  return <PreferencesContext.Provider value={{ language, theme, setLanguage: changeLanguage, toggleTheme }}><div className="dashboard-shell min-h-screen bg-ink text-slate-100">
    <header className="fixed inset-x-0 top-0 z-[60] flex h-[64px] items-center gap-4 border-b border-line/70 bg-ink/95 px-4 shadow-lg shadow-black/10 backdrop-blur-xl sm:px-6">
      <button ref={menuButtonRef} type="button" aria-expanded={drawer} aria-controls="student-dashboard-sidebar" aria-label="Open dashboard navigation" onClick={() => setDrawer(true)} className="rounded-xl p-2 text-slate-400 hover:bg-surface hover:text-white lg:hidden"><Menu size={20} /></button>
      <Link href="/dashboard" aria-label="Languages-Platform dashboard" className="hidden items-center gap-2 text-sm font-bold sm:flex"><Image src="/branding/tkp.png" alt="Languages-Platform logo" width={32} height={32} className="h-8 w-8 object-contain" priority /><span>Languages-Platform</span></Link>
      <div className="relative min-w-0 flex-1 md:max-w-xl md:flex-none"><Search className="absolute left-3 top-2.5 text-slate-500" size={17} /><input aria-label={text.search} value={query} onChange={event => setQuery(event.target.value)} onKeyDown={event => { if (event.key === "Enter" && query.trim()) window.location.href = `/courses?search=${encodeURIComponent(query.trim())}`; }} placeholder={text.search} className="w-full rounded-xl border border-line/70 bg-surface/70 py-2.5 pl-10 pr-9 text-sm text-slate-200 placeholder:text-slate-500 focus:border-indigo-400 focus:outline-none" />{query && <button type="button" aria-label="Clear search" onClick={() => setQuery("")} className="absolute right-2 top-2 rounded-lg p-1 text-slate-500 hover:text-white"><X size={15} /></button>}{query.trim().length >= 2 && <div role="region" aria-label="Search results" className="absolute inset-x-0 top-12 z-50 rounded-xl border border-line bg-surface p-2 shadow-2xl">{searching ? <p className="p-3 text-sm text-slate-400">Searching…</p> : results.length ? results.map(course => <Link key={course.id} href={`/courses/${course.slug}`} onClick={() => setQuery("")} className="block rounded-lg p-3 text-sm hover:bg-elevated"><span className="font-medium">{course.title}</span><span className="mt-1 block text-xs text-slate-500">{course.language.name} · {course.level}</span></Link>) : <p className="p-3 text-sm text-slate-500">No published courses found.</p>}</div>}</div>
      <div className="ml-auto flex items-center gap-1 sm:gap-2"><button type="button" aria-label={text.theme} onClick={toggleTheme} className="hidden rounded-xl p-2 text-slate-400 hover:bg-surface hover:text-white sm:block">{theme === "dark" ? <Eye size={18} /> : <EyeOff size={18} />}</button><button type="button" aria-label={text.language} onClick={() => changeLanguage(language === "en" ? "my" : "en")} className="rounded-xl px-2 py-2 text-xs font-semibold text-slate-400 hover:bg-surface hover:text-white">{language === "en" ? "EN / MM" : "MM / EN"}</button><Link aria-label={text.notifications} href="/settings/notifications" className="rounded-xl p-2 text-slate-400 hover:bg-surface hover:text-white"><Sparkles size={18} /></Link><div className="relative"><button type="button" aria-haspopup="menu" aria-expanded={profileOpen} aria-label={text.profileMenu} onClick={() => setProfileOpen(value => !value)} className="flex items-center gap-2 rounded-xl p-1.5 text-sm hover:bg-surface"><span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-indigo-400 to-violet-600 text-xs font-bold">CM</span><span className="hidden text-slate-300 lg:inline">{text.profile}</span></button>{profileOpen && <div role="menu" className="absolute right-0 top-12 z-50 w-44 rounded-xl border border-line bg-surface p-2 shadow-2xl"><Link role="menuitem" href="/profile" onClick={() => setProfileOpen(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-elevated">{text.profile}</Link><Link role="menuitem" href="/settings" onClick={() => setProfileOpen(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-elevated">{text.settings}</Link><div className="my-1 border-t border-line" /><LogoutButton /></div>}</div></div>
    </header>
    <div className="h-[64px]" aria-hidden="true" />
    <div className="flex">
      {drawer && <button type="button" aria-label="Close dashboard navigation overlay" onClick={() => setDrawer(false)} className="fixed inset-0 z-40 bg-black/60 lg:hidden" />}
      <aside ref={drawerRef} id="student-dashboard-sidebar" className={`${drawer ? "translate-x-0 z-50" : "-translate-x-full z-30"} ${collapsed ? "lg:w-[68px]" : "lg:w-[250px]"} fixed bottom-0 left-0 top-0 w-[280px] shrink-0 border-r border-line/70 bg-[#10182c] px-3 pt-4 transition-all lg:bottom-0 lg:top-[64px] lg:translate-x-0 lg:overflow-y-auto`}>
        <div className="mb-5 flex items-center justify-between px-2 lg:justify-end"><span className="text-xs font-semibold uppercase tracking-[.18em] text-slate-500 lg:hidden">Learn</span><button type="button" aria-label="Close navigation" onClick={() => setDrawer(false)} className="rounded-lg p-2 text-slate-400 hover:bg-surface lg:hidden"><X size={18} /></button><button type="button" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} onClick={toggle} className="hidden rounded-lg p-2 text-slate-400 hover:bg-surface hover:text-white lg:block"><ArrowRight size={18} /></button></div>
        <nav aria-label="Student dashboard" className="space-y-1">{items.map(([_, href, Icon], index) => { const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`)); const group = href === "/dashboard" ? text.main : href === "/dashboard/analytics" ? text.tools : href === "/settings/notifications" ? text.community : href === "/profile" ? text.account : null; return <div key={href}>{group && !collapsed && <p className="mb-2 mt-5 px-3 text-[10px] font-semibold uppercase tracking-[.18em] text-slate-600">{group}</p>}<Link href={href} onClick={() => setDrawer(false)} title={collapsed ? navLabels[index] : undefined} className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${active ? "bg-indigo-500/20 text-indigo-200" : "text-slate-400 hover:bg-white/[.05] hover:text-slate-100"}`}><Icon size={18} className="shrink-0" /><span className={collapsed ? "lg:hidden" : ""}>{navLabels[index]}</span>{active && !collapsed && <ArrowRight className="ml-auto" size={15} />}</Link></div>; })}</nav>
        {!collapsed && <div className="mt-8 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-500/5 p-4"><p className="text-sm font-semibold text-indigo-100">{text.momentum}</p><p className="mt-2 text-xs leading-5 text-slate-400">Complete a lesson today to grow your verified learning streak.</p><Link href="/courses" className="mt-4 inline-flex text-xs font-semibold text-indigo-300 hover:text-white">{text.browse} <ArrowRight size={14} /></Link></div>}
      </aside>
      <main className={`${collapsed ? "lg:ml-[68px]" : "lg:ml-[250px]"} dashboard-main min-w-0 flex-1 px-4 py-7 sm:px-6 lg:px-10 lg:py-8`}>{children}</main>
    </div>
  </div></PreferencesContext.Provider>;
}
