"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Bell,
  BookOpen,
  Code2,
  FolderKanban,
  Gauge,
  GraduationCap,
  Images,
  Languages,
  LayoutDashboard,
  Menu,
  PanelLeftClose,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Tags,
  Terminal,
  Users,
  Wrench,
  X,
  type LucideIcon,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { adminApi } from "@/lib/api";
import { csrf } from "@/components/auth-form";
import { LanguageSwitcher } from "@/components/language-switcher";
import { Card, Skeleton } from "@/components/ui";
import { useI18n } from "@/lib/i18n";

type ManagementUser = {
  full_name: string;
  role: string;
};

type ManagementNavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  roles?: string[];
};

type ManagementNavGroup = {
  title: string;
  items: ManagementNavItem[];
};

const PLATFORM_ROLES = ["admin", "platform_admin", "super_admin"];
const CONTENT_ROLES = [...PLATFORM_ROLES, "instructor", "content_editor"];

const groups: ManagementNavGroup[] = [
  {
    title: "Workspace",
    items: [
      { label: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard, roles: PLATFORM_ROLES },
      { label: "Courses", href: "/admin/courses", icon: BookOpen, roles: CONTENT_ROLES },
      { label: "Curriculum Quality", href: "/admin/curriculum-quality", icon: BarChart3, roles: PLATFORM_ROLES },
      { label: "Challenges", href: "/admin/challenges", icon: Code2, roles: CONTENT_ROLES },
      { label: "Projects", href: "/admin/projects", icon: FolderKanban, roles: CONTENT_ROLES },
      { label: "Learning Paths", href: "/admin/roadmaps", icon: GraduationCap, roles: PLATFORM_ROLES },
    ],
  },
  {
    title: "Content operations",
    items: [
      { label: "Content Studio", href: "/platform/content-studio", icon: Terminal, roles: PLATFORM_ROLES },
      { label: "Content Review", href: "/platform/content-review", icon: ShieldCheck, roles: PLATFORM_ROLES },
      { label: "Syntax References", href: "/admin/courses", icon: Code2, roles: CONTENT_ROLES },
      { label: "Media Library", href: "/platform/media", icon: Images, roles: PLATFORM_ROLES },
      { label: "Translations", href: "/admin/translations", icon: Languages, roles: PLATFORM_ROLES },
      { label: "Categories", href: "/admin/categories", icon: Tags, roles: PLATFORM_ROLES },
    ],
  },
  {
    title: "People & insights",
    items: [
      { label: "Students", href: "/platform/students", icon: Users, roles: PLATFORM_ROLES },
      { label: "Instructors", href: "/platform/instructors", icon: GraduationCap, roles: PLATFORM_ROLES },
      { label: "Analytics", href: "/platform/analytics", icon: BarChart3, roles: PLATFORM_ROLES },
      { label: "Reports", href: "/platform/reports", icon: Activity, roles: PLATFORM_ROLES },
      { label: "Notifications", href: "/platform/notifications", icon: Bell, roles: PLATFORM_ROLES },
    ],
  },
  {
    title: "Platform governance",
    items: [
      { label: "Admin Users", href: "/admin/users", icon: Users, roles: PLATFORM_ROLES },
      { label: "Audit Logs", href: "/admin/audit-logs", icon: Activity, roles: PLATFORM_ROLES },
      { label: "General Settings", href: "/platform/settings", icon: Settings, roles: PLATFORM_ROLES },
      { label: "Branding", href: "/admin/settings", icon: SlidersHorizontal, roles: PLATFORM_ROLES },
      { label: "AI Operations", href: "/admin/ai", icon: Wrench, roles: PLATFORM_ROLES },
      { label: "System Health", href: "/platform/system-health", icon: Gauge, roles: PLATFORM_ROLES },
      { label: "Security", href: "/platform/security", icon: ShieldCheck, roles: PLATFORM_ROLES },
    ],
  },
];

function isActive(pathname: string, href: string) {
  return href === "/admin/dashboard" || href === "/platform" || href === "/platform/analytics"
    ? pathname === href
    : pathname === href || pathname.startsWith(`${href}/`);
}

export function ManagementShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLogin = pathname === "/admin/login" || pathname === "/platform/login";
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<ManagementUser | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  const loadSession = useCallback(() => {
    if (isLogin) return;
    setError("");
    adminApi
      .me()
      .then((value) => setUser(value))
      .catch((reason) => {
        setError(reason instanceof Error ? reason.message : "Administrator session unavailable");
      });
  }, [isLogin]);

  useEffect(() => {
    setCollapsed(window.localStorage.getItem("cm-management-sidebar-collapsed") === "1");
  }, []);

  useEffect(() => {
    loadSession();
  }, [loadSession, retry]);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", close);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", close);
      document.body.style.overflow = "";
    };
  }, [open]);

  const visibleGroups = useMemo(
    () => groups
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => !item.roles || (user && item.roles.includes(user.role))),
      }))
      .filter((group) => group.items.length),
    [user],
  );

  const toggleCollapse = () => {
    setCollapsed((value) => {
      const next = !value;
      window.localStorage.setItem("cm-management-sidebar-collapsed", next ? "1" : "0");
      return next;
    });
  };

  const logout = async () => {
    try {
      await adminApi.logout(csrf());
    } finally {
      window.location.href = "/admin/login";
    }
  };

  if (isLogin) return <>{children}</>;

  if (error) {
    return (
      <div className="grid min-h-screen place-items-center bg-ink px-5">
        <Card className="w-full max-w-md p-7">
          <ShieldCheck className="h-8 w-8 text-rose-300" />
          <h1 className="mt-4 text-xl font-semibold">Management access unavailable</h1>
          <p className="mt-2 text-sm leading-6 text-slate-400">{error}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <button type="button" onClick={() => setRetry((value) => value + 1)} className="rounded-xl border border-line px-4 py-2.5 text-sm font-semibold text-slate-200 hover:bg-surface">Retry connection</button>
            <Link href="/admin/login" className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500">Sign in</Link>
          </div>
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-ink p-5">
        <Skeleton className="mx-auto h-14 max-w-[1600px]" />
        <div className="mx-auto mt-6 grid max-w-[1600px] gap-4 lg:grid-cols-[264px_1fr]">
          <Skeleton className="h-[720px]" />
          <Skeleton className="h-[720px]" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080d1b] text-slate-100">
      <header className="sticky top-0 z-40 border-b border-white/[.07] bg-[#0b1120]/95 shadow-[0_10px_35px_rgba(2,6,23,.22)] backdrop-blur-xl">
        <div className="mx-auto flex h-[68px] max-w-[1600px] items-center gap-3 px-4 sm:px-6 lg:px-0">
          <div className={`flex shrink-0 items-center gap-3 transition-[width] duration-200 ${collapsed ? "lg:w-[76px] lg:justify-center" : "lg:w-[264px]"}`}>
            <button type="button" aria-label="Open management navigation" onClick={() => setOpen(true)} className="rounded-xl p-2 text-slate-400 hover:bg-white/[.06] hover:text-white lg:hidden"><Menu size={19} /></button>
            <Link href="/admin/dashboard" className="flex min-w-0 items-center gap-3 font-semibold">
              <Image src="/branding/tkp.png" alt="TKP logo" width={36} height={36} className="h-9 w-9 shrink-0 rounded-xl object-contain" />
              <span className={`truncate text-[15px] tracking-tight ${collapsed ? "lg:hidden" : ""}`}>Learn-Coding <span className="text-indigo-300">Management</span></span>
            </Link>
          </div>
          <div className="hidden min-w-0 flex-1 justify-center px-6 md:flex">
            <label className="flex h-10 w-full max-w-[580px] items-center gap-3 rounded-xl border border-white/[.07] bg-white/[.035] px-3.5 text-sm text-slate-500 focus-within:border-indigo-400/50 focus-within:bg-white/[.055]">
              <Search size={16} />
              <input aria-label="Search management workspace" placeholder="Search courses, students, reports…" className="w-full bg-transparent text-slate-200 outline-none placeholder:text-slate-600" />
            </label>
          </div>
          <div className="ml-auto flex items-center gap-1.5 sm:gap-3">
            <LanguageSwitcher />
            <div className="hidden h-8 w-px bg-white/[.08] sm:block" />
            <span className="hidden text-right sm:block"><span className="block max-w-48 truncate text-sm font-semibold">{user.full_name}</span><span className="mt-0.5 block text-[11px] capitalize text-slate-500">{user.role.replaceAll("_", " ")}</span></span>
            <button type="button" onClick={logout} className="rounded-xl px-3 py-2 text-sm font-medium text-slate-400 hover:bg-white/[.06] hover:text-white">{t("logout")}</button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex min-h-[calc(100vh-68px)] max-w-[1600px]">
        <aside className={`fixed inset-y-0 left-0 z-50 w-[264px] transform border-r border-white/[.07] bg-[#0e1729] px-3.5 pb-6 pt-5 transition-[transform,width] duration-200 lg:sticky lg:top-[68px] lg:z-0 lg:h-[calc(100vh-68px)] lg:min-h-[calc(100vh-68px)] lg:translate-x-0 lg:overflow-y-auto ${collapsed ? "lg:w-[76px]" : "lg:w-[264px]"} ${open ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="mb-5 flex items-center justify-between px-2 lg:hidden"><span className="font-semibold">Navigation</span><button type="button" aria-label="Close management navigation" onClick={() => setOpen(false)} className="rounded-lg p-2 text-slate-400 hover:bg-white/[.06] hover:text-white"><X size={20} /></button></div>
          <div className={`mb-5 hidden items-center ${collapsed ? "lg:justify-center" : "lg:justify-between"} lg:flex`}><span className={`text-[10px] font-bold uppercase tracking-[.18em] text-slate-600 ${collapsed ? "lg:hidden" : ""}`}>Management workspace</span><button type="button" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} title={collapsed ? "Expand sidebar" : "Collapse sidebar"} onClick={toggleCollapse} className="rounded-lg p-2 text-slate-500 hover:bg-white/[.06] hover:text-slate-100"><PanelLeftClose size={17} /></button></div>
          <nav aria-label="Management navigation" className="space-y-7">{visibleGroups.map((group) => <div key={group.title}><p className={`mb-2 px-3 text-[10px] font-bold uppercase tracking-[.2em] text-slate-600 ${collapsed ? "lg:hidden" : ""}`}>{group.title}</p><div className="space-y-1">{group.items.map(({ label, href, icon: Icon }) => { const active = isActive(pathname, href); return <Link key={`${label}-${href}`} href={href} title={collapsed ? label : undefined} onClick={() => setOpen(false)} aria-current={active ? "page" : undefined} className={`group flex h-10 items-center gap-3 rounded-xl px-3 text-[13px] font-medium transition ${active ? "bg-indigo-500/15 text-indigo-100 shadow-[inset_3px_0_0_#818cf8]" : "text-slate-400 hover:bg-white/[.05] hover:text-slate-100"} ${collapsed ? "lg:justify-center lg:px-2" : ""}`}><Icon size={16} className={`shrink-0 ${active ? "text-indigo-300" : "text-slate-500 group-hover:text-slate-300"}`} /><span className={collapsed ? "lg:hidden" : ""}>{label}</span>{active && !collapsed && <span className="ml-auto text-indigo-300">›</span>}</Link>; })}</div></div>)}</nav>
        </aside>
        {open && <button type="button" aria-label="Close management navigation overlay" onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" />}
        <main className="min-w-0 flex-1 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,.09),transparent_34rem)] px-5 py-7 sm:px-7 lg:px-10 lg:py-9"><div className="mx-auto w-full max-w-[1420px]">{children}</div></main>
      </div>
    </div>
  );
}
