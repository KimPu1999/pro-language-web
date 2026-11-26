"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity, BarChart3, Bell, BookOpen, BriefcaseBusiness, ChevronRight,
  CircleAlert, Code2, DatabaseBackup, Flag, FolderKanban, Gauge,
  GraduationCap, Images, LayoutDashboard, LifeBuoy, Menu, MessageSquare,
  PanelLeftClose, Rocket, Search, Settings, ShieldCheck, SlidersHorizontal,
  Sparkles, Users, Wrench, X, type LucideIcon,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LogoutButton } from "@/components/auth-form";
import { Card, Skeleton } from "@/components/ui";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useI18n } from "@/lib/i18n";

type NavItem = { label: string; href: string; icon: LucideIcon };
type NavGroup = { label: string; items: NavItem[] };

const navGroups: NavGroup[] = [
  { label: "Workspace", items: [
    { label: "Overview", href: "/platform", icon: LayoutDashboard },
    { label: "Courses", href: "/platform/courses", icon: BookOpen },
    { label: "Learning Paths", href: "/platform/learning-paths", icon: GraduationCap },
    { label: "Challenges", href: "/platform/challenges", icon: Code2 },
    { label: "Projects", href: "/platform/projects", icon: FolderKanban },
  ] },
  { label: "People & content", items: [
    { label: "Community", href: "/platform/community", icon: MessageSquare },
    { label: "Students", href: "/platform/students", icon: Users },
    { label: "Instructors", href: "/platform/instructors", icon: BriefcaseBusiness },
    { label: "Content Review", href: "/platform/content-review", icon: Sparkles },
    { label: "Media Library", href: "/platform/media", icon: Images },
  ] },
  { label: "Insights", items: [
    { label: "Analytics", href: "/platform/analytics", icon: BarChart3 },
    { label: "Notifications", href: "/platform/notifications", icon: Bell },
    { label: "System Health", href: "/platform/system-health", icon: Gauge },
    { label: "Monitoring", href: "/platform/monitoring", icon: Activity },
    { label: "Incidents", href: "/platform/incidents", icon: CircleAlert },
  ] },
  { label: "Operations", items: [
    { label: "Operations", href: "/platform/operations", icon: Wrench },
    { label: "Releases", href: "/platform/releases", icon: Rocket },
    { label: "Feature Flags", href: "/platform/feature-flags", icon: Flag },
    { label: "Maintenance", href: "/platform/maintenance", icon: SlidersHorizontal },
    { label: "Backups", href: "/platform/backups", icon: DatabaseBackup },
    { label: "Settings", href: "/platform/settings", icon: Settings },
  ] },
];

function isActive(pathname: string, href: string) {
  return href === "/platform" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);
}

export function PlatformShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState("");
  const isLogin = pathname === "/platform/login";
  const { t } = useI18n();
  const labelText = (label: string) => ({ Workspace: t("workspace"), "People & content": t("peopleContent"), Insights: t("insights"), Operations: t("operations"), Overview: t("dashboard"), Courses: t("courses"), "Learning Paths": t("learningPaths"), Challenges: t("challenges"), Projects: t("projects"), Community: t("community"), Students: t("students"), Instructors: t("instructors"), "Content Review": t("contentReview"), "Media Library": t("mediaLibrary"), Analytics: t("analytics"), Notifications: t("notifications"), Settings: t("settings") }[label] ?? label);

  const refreshSession = useCallback(() => {
    if (isLogin) return;
    api.me().then((nextUser) => { setUser(nextUser); setError(""); }).catch((e) => setError(e.message));
  }, [isLogin]);

  useEffect(() => {
    refreshSession();
    window.addEventListener("focus", refreshSession);
    return () => window.removeEventListener("focus", refreshSession);
  }, [refreshSession]);

  useEffect(() => setOpen(false), [pathname]);

  if (isLogin) return <>{children}</>;
  if (error) return <div className="grid min-h-screen place-items-center bg-ink px-5"><Card className="max-w-md p-7"><ShieldCheck className="h-8 w-8 text-indigo-300"/><h1 className="mt-4 text-xl font-semibold">Platform access unavailable</h1><p className="mt-2 text-sm leading-6 text-slate-400">{error}</p><Link href="/platform/login" className="mt-5 inline-block rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold">Go to admin login</Link></Card></div>;
  if (!user) return <div className="min-h-screen bg-ink p-5"><Skeleton className="mx-auto mt-8 h-16 max-w-[1500px]"/><div className="mx-auto mt-6 grid max-w-[1500px] gap-4 lg:grid-cols-[280px_1fr]"><Skeleton className="h-[680px]"/><Skeleton className="h-[680px]"/></div></div>;

  const allowed = user.email_verified && ["platform_admin", "admin", "super_admin"].includes(user.role);
  if (!allowed) return <div className="grid min-h-screen place-items-center bg-ink px-5"><Card className="max-w-md p-7"><ShieldCheck className="h-8 w-8 text-amber-300"/><h1 className="mt-4 text-xl font-semibold">Administrator access required</h1><p className="mt-2 text-sm leading-6 text-slate-400">Your account is authenticated, but it does not have platform-admin permissions.</p><Link href="/dashboard" className="mt-5 inline-block rounded-xl bg-elevated px-4 py-2.5 text-sm font-semibold">Return to dashboard</Link></Card></div>;

  return <div className="min-h-screen bg-ink text-slate-100">
    <header className="sticky top-0 z-40 border-b border-line/80 bg-[#0d1424]/95 shadow-[0_8px_30px_rgba(2,6,23,.18)] backdrop-blur-xl">
      <div className="flex h-[72px] items-center gap-3 px-4 sm:px-6 lg:px-8">
        <button aria-label="Open navigation" onClick={() => setOpen(true)} className="rounded-xl p-2.5 text-slate-400 transition hover:bg-surface hover:text-white lg:hidden"><Menu size={20}/></button>
        <Link href="/platform" className="flex min-w-0 items-center gap-3 lg:w-[280px] lg:shrink-0"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-indigo-400 to-violet-600 shadow-lg shadow-indigo-500/20"><ShieldCheck size={19}/></span><span className="truncate text-[15px] font-bold tracking-tight">Platform Control Center</span></Link>
        <div className="hidden min-w-0 flex-1 justify-center px-6 md:flex"><label className="flex h-11 w-full max-w-[580px] items-center gap-3 rounded-xl border border-line/70 bg-surface/70 px-4 text-sm text-slate-500 transition focus-within:border-indigo-400/60 focus-within:bg-surface"><Search size={17}/><input aria-label="Global search" placeholder="Search platform content…" className="w-full bg-transparent text-slate-200 outline-none placeholder:text-slate-500"/><kbd className="hidden rounded-md border border-line bg-ink/60 px-2 py-0.5 text-[10px] text-slate-500 xl:inline">⌘ K</kbd></label></div>
        <div className="ml-auto flex items-center gap-1.5 sm:gap-3"><Link aria-label="System health" href="/platform/system-health" className="hidden rounded-xl p-2.5 text-slate-400 transition hover:bg-surface hover:text-white sm:block"><Activity size={18}/></Link><Link aria-label="Notifications" href="/platform/notifications" className="rounded-xl p-2.5 text-slate-400 transition hover:bg-surface hover:text-white"><Bell size={18}/></Link><LanguageSwitcher/><div className="hidden h-8 w-px bg-line sm:block"/><span className="hidden text-right sm:block"><span className="block max-w-44 truncate text-sm font-semibold">{user.full_name}</span><span className="mt-0.5 block text-[11px] capitalize text-slate-500">{user.role.replaceAll("_", " ")}</span></span><Link href="/" className="hidden rounded-lg px-2 py-2 text-sm text-slate-400 transition hover:bg-surface hover:text-white lg:block">View site ↗</Link><LogoutButton/></div>
      </div>
    </header>

    <div className="flex min-h-[calc(100vh-72px)]">
      <aside className={`fixed inset-y-0 left-0 z-50 w-[280px] transform border-r border-line/80 bg-[#0d1424] px-4 pb-6 pt-5 transition-transform lg:sticky lg:top-[72px] lg:z-0 lg:h-[calc(100vh-72px)] lg:translate-x-0 lg:overflow-y-auto ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-5 flex items-center justify-between px-2 lg:hidden"><span className="text-sm font-semibold">Navigation</span><button aria-label="Close navigation" onClick={() => setOpen(false)} className="rounded-lg p-2 text-slate-400 hover:bg-surface hover:text-white"><X size={19}/></button></div>
        <div className="mb-5 rounded-xl border border-indigo-400/10 bg-gradient-to-br from-indigo-500/10 to-transparent px-3.5 py-3"><div className="flex items-center gap-2 text-xs font-semibold text-indigo-200"><PanelLeftClose size={15}/><span>{t("adminWorkspace")}</span></div><p className="mt-1 text-[11px] leading-5 text-slate-500">{t("managePlatform")}</p></div>
        <nav aria-label="Platform navigation" className="space-y-5">{navGroups.map(group => <div key={group.label}><p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-600">{labelText(group.label)}</p><div className="space-y-1">{group.items.map(({ label, href, icon: Icon }) => { const active = isActive(pathname, href); return <Link key={href} href={href} onClick={() => setOpen(false)} aria-current={active ? "page" : undefined} className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition ${active ? "bg-indigo-500/15 text-indigo-200 shadow-[inset_3px_0_0_#818cf8]" : "text-slate-400 hover:bg-surface/80 hover:text-slate-100"}`}><Icon size={16} className={active ? "text-indigo-300" : "text-slate-500 group-hover:text-slate-300"}/><span className="flex-1">{labelText(label)}</span>{active && <ChevronRight size={14} className="text-indigo-300"/>}</Link>; })}</div></div>)}</nav>
        <div className="mt-8 rounded-xl border border-line/70 bg-surface/40 p-3"><div className="flex items-center gap-2 text-xs font-semibold text-slate-300"><LifeBuoy size={15} className="text-slate-500"/> Need help?</div><p className="mt-1.5 text-[11px] leading-5 text-slate-500">Check system health before opening an incident.</p><Link href="/platform/system-health" className="mt-2 inline-flex text-xs font-semibold text-indigo-300 hover:text-indigo-200">View health →</Link></div>
      </aside>
      {open && <button aria-label="Close navigation overlay" onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm lg:hidden"/>}
      <main className="min-w-0 flex-1 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,.08),transparent_32rem)] px-4 py-7 sm:px-6 lg:px-10 lg:py-9"><div className="mx-auto w-full max-w-[1440px]">{children}</div></main>
    </div>
  </div>;
}
