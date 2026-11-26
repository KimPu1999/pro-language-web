"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BookOpen, Code2, Languages, LayoutDashboard, Menu, Search, Tags, Terminal, X } from "lucide-react";
import { useEffect, useState } from "react";
import { adminApi } from "@/lib/api";
import { csrf } from "@/components/auth-form";
import { Card, Skeleton } from "@/components/ui";

const groups = [
  { title: "Workspace", items: [["Dashboard", "/admin/dashboard", LayoutDashboard], ["Course Management", "/admin/courses", BookOpen], ["Curriculum Quality", "/admin/curriculum-quality", BarChart3], ["Module Management", "/platform/content-studio", Code2], ["Lesson Management", "/platform/content-studio", Code2], ["Quiz Management", "/platform/assessment-integrity", Terminal], ["Project Management", "/admin/projects", Code2]] as const },
  { title: "Platform", items: [["Students", "/platform/students", Code2], ["Instructors", "/platform/instructors", Code2], ["Categories", "/admin/categories", Tags], ["Media Library", "/platform/media", Code2], ["Analytics & Reports", "/platform/reports", BarChart3], ["Announcements", "/platform/notifications", Languages]] as const },
  { title: "Governance", items: [["Admin Users", "/platform/settings", Code2], ["Audit Logs", "/platform/security", Terminal], ["Settings", "/admin/settings", Tags]] as const },
];

function isActive(pathname: string, href: string) { return pathname === href || pathname.startsWith(`${href}/`); }

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<{ full_name: string; role: string } | null>(null);
  const [error, setError] = useState("");
  const isLogin = pathname === "/admin/login";
  useEffect(() => { setCollapsed(window.localStorage.getItem("cm-admin-sidebar-collapsed") === "1"); }, []);
  useEffect(() => { if (!open) return; const close = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); }; document.addEventListener("keydown", close); document.body.style.overflow = "hidden"; return () => { document.removeEventListener("keydown", close); document.body.style.overflow = ""; }; }, [open]);
  useEffect(() => { if (isLogin) return; adminApi.me().then(setUser).catch((err) => setError(err instanceof Error ? err.message : "Admin session unavailable")); }, [isLogin]);
  if (isLogin) return <>{children}</>;
  if (error) return <div className="grid min-h-screen place-items-center bg-ink px-5"><Card className="max-w-md p-7"><p className="text-sm text-red-300">Admin session unavailable</p><p className="mt-3 text-sm leading-6 text-slate-400">{error}</p><Link href="/admin/login" className="mt-5 inline-block rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white">Go to admin login</Link></Card></div>;
  if (!user) return <div className="min-h-screen bg-ink p-5"><Skeleton className="mx-auto h-14 max-w-7xl"/><div className="mx-auto mt-6 grid max-w-7xl gap-4 lg:grid-cols-[250px_1fr]"><Skeleton className="h-[700px]"/><Skeleton className="h-[700px]"/></div></div>;
  const toggleCollapse = () => setCollapsed(value => { const next = !value; window.localStorage.setItem("cm-admin-sidebar-collapsed", next ? "1" : "0"); return next; });
  const logout = async () => { try { await adminApi.logout(csrf()); } finally { window.location.href = "/admin/login"; } };
  return <div className="min-h-screen bg-ink text-slate-100"><header className="sticky top-0 z-40 border-b border-line/80 bg-ink/90 backdrop-blur-xl"><div className="flex h-16 items-center gap-3 px-4 lg:px-6"><button aria-label="Open admin navigation" onClick={() => setOpen(true)} className="rounded-lg p-2 hover:bg-surface lg:hidden"><Menu size={19}/></button><Link href="/admin/dashboard" className="flex min-w-0 items-center gap-3 font-semibold"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-primary"><Code2 size={18}/></span><span className="truncate">Admin Control Center</span></Link><div className="hidden min-w-0 flex-1 justify-center px-8 md:flex"><label className="flex w-full max-w-xl items-center gap-3 rounded-xl bg-surface px-4 py-2 text-sm text-slate-500"><Search size={16}/><input aria-label="Search admin content" placeholder="Search courses, students, reports…" className="w-full bg-transparent outline-none"/></label></div><div className="ml-auto flex items-center gap-3"><span className="hidden text-right sm:block"><span className="block text-sm font-medium">{user.full_name}</span><span className="block text-xs capitalize text-slate-500">{user.role.replaceAll("_", " ")}</span></span><button onClick={logout} className="rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-surface hover:text-white">Log out</button></div></div></header><div className="mx-auto flex max-w-[1600px]"><aside className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-line bg-[#10182C] px-3 pt-5 transition-transform lg:sticky lg:top-16 lg:z-0 lg:h-[calc(100vh-4rem)] lg:translate-x-0 lg:shrink-0 lg:overflow-y-auto lg:pt-5 ${collapsed ? "lg:w-[76px]" : "lg:w-64"} ${open ? "translate-x-0" : "-translate-x-full"}`}><div className="mb-5 flex items-center justify-between px-2 lg:hidden"><span className="font-semibold">Navigation</span><button aria-label="Close admin navigation" onClick={() => setOpen(false)}><X size={20}/></button></div><div className="mb-4 hidden justify-end lg:flex"><button aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} title={collapsed ? "Expand sidebar" : "Collapse sidebar"} onClick={toggleCollapse} className="rounded-lg p-2 text-slate-400 hover:bg-surface hover:text-white"><BarChart3 size={17}/></button></div><nav className="space-y-5">{groups.map(group => <div key={group.title}><p className={`mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 ${collapsed ? "lg:hidden" : ""}`}>{group.title}</p><div className="space-y-1">{group.items.map(([label, href, Icon]) => <Link key={`${label}-${href}`} href={href} title={collapsed ? label : undefined} onClick={() => setOpen(false)} className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive(pathname, href) ? "bg-primary/20 text-indigo-200" : "text-slate-400 hover:bg-surface hover:text-white"} ${collapsed ? "lg:justify-center lg:px-2" : ""}`}><Icon size={17} className="shrink-0"/><span className={collapsed ? "lg:hidden" : ""}>{label}</span>{isActive(pathname, href) && !collapsed && <span className="ml-auto text-xs">›</span>}</Link>)}</div></div>)}</nav></aside>{open && <button aria-label="Close admin navigation overlay" onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-black/60 lg:hidden"/>}<main className="min-w-0 flex-1 px-4 py-7 lg:px-8">{children}</main></div></div>;
}
