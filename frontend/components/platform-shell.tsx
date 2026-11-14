"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3 as Bell, BarChart3 as ChevronRight, BarChart3 as LogOut, Menu, Search, BarChart3 as ShieldCheck, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LogoutButton } from "@/components/auth-form";
import { Card, Skeleton } from "@/components/ui";

const links = [
  ["Overview", "/platform"],
  ["Courses", "/platform/courses"],
  ["Learning Paths", "/platform/learning-paths"],
  ["Challenges", "/platform/challenges"],
  ["Projects", "/platform/projects"],
  ["Community", "/platform/community"],
  ["Students", "/platform/students"],
  ["Instructors", "/platform/instructors"],
  ["Content Review", "/platform/content-review"],
  ["Analytics", "/platform/analytics"],
  ["Notifications", "/platform/notifications"],
  ["Media Library", "/platform/media"],
  ["Security Center", "/platform/security"],
  ["System Health", "/platform/system-health"],
  ["Operations", "/platform/operations"],
  ["Monitoring", "/platform/monitoring"],
  ["Incidents", "/platform/incidents"],
  ["Improvements", "/platform/improvements"],
  ["Releases", "/platform/releases"],
  ["Feature Flags", "/platform/feature-flags"],
  ["Maintenance", "/platform/maintenance"],
  ["Backups", "/platform/backups"],
  ["Settings", "/platform/settings"],
] as const;

export function PlatformShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState("");
  const isLogin = pathname === "/platform/login";
  const refreshSession = useCallback(() => {
    if (isLogin) return;
    api.me().then((nextUser) => { setUser(nextUser); setError(""); }).catch((e) => setError(e.message));
  }, [isLogin]);
  useEffect(() => {
    refreshSession();
    window.addEventListener("focus", refreshSession);
    return () => window.removeEventListener("focus", refreshSession);
  }, [refreshSession]);
  if (isLogin) return <>{children}</>;
  if (error) return <div className="grid min-h-screen place-items-center bg-ink px-5"><Card className="max-w-md p-7"><ShieldCheck className="h-8 w-8 text-indigo-300"/><h1 className="mt-4 text-xl font-semibold">Platform access unavailable</h1><p className="mt-2 text-sm leading-6 text-slate-400">{error}</p><Link href="/platform/login" className="mt-5 inline-block rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold">Go to admin login</Link></Card></div>;
  if (!user) return <div className="min-h-screen bg-ink p-5"><Skeleton className="mx-auto mt-8 h-14 max-w-7xl"/><div className="mx-auto mt-6 grid max-w-7xl gap-4 lg:grid-cols-[220px_1fr]"><Skeleton className="h-[600px]"/><Skeleton className="h-[600px]"/></div></div>;
  // This is only a UX guard. Every platform API endpoint independently
  // enforces the same role on the server.
  const allowed = user.email_verified && ["platform_admin", "admin", "super_admin"].includes(user.role);
  if (!allowed) return <div className="grid min-h-screen place-items-center bg-ink px-5"><Card className="max-w-md p-7"><ShieldCheck className="h-8 w-8 text-amber-300"/><h1 className="mt-4 text-xl font-semibold">Administrator access required</h1><p className="mt-2 text-sm leading-6 text-slate-400">Your account is authenticated, but it does not have platform-admin permissions.</p><Link href="/dashboard" className="mt-5 inline-block rounded-xl bg-elevated px-4 py-2.5 text-sm font-semibold">Return to dashboard</Link></Card></div>;
  return <div className="min-h-screen bg-ink text-slate-100"><header className="sticky top-0 z-40 border-b border-line/80 bg-ink/90 backdrop-blur-xl"><div className="flex h-16 items-center justify-between gap-4 px-4 lg:px-6"><button aria-label="Open navigation" onClick={() => setOpen(true)} className="rounded-lg p-2 hover:bg-surface lg:hidden"><Menu size={20}/></button><Link href="/platform" className="flex items-center gap-3 font-semibold"><span className="grid h-9 w-9 place-items-center rounded-xl bg-primary"><ShieldCheck size={18}/></span><span className="hidden sm:inline">Platform Control Center</span><span className="sm:hidden">Control Center</span></Link><div className="hidden min-w-0 flex-1 items-center justify-center px-8 md:flex"><label className="flex w-full max-w-xl items-center gap-3 rounded-xl bg-surface px-4 py-2 text-sm text-slate-500"><Search size={16}/><input aria-label="Global search" placeholder="Search platform content…" className="w-full bg-transparent outline-none"/></label></div><div className="flex items-center gap-3"><Link aria-label="Notifications" href="/platform/notifications" className="rounded-lg p-2 text-slate-400 hover:bg-surface hover:text-white"><Bell size={18}/></Link><span className="hidden text-right sm:block"><span className="block text-sm font-medium">{user.full_name}</span><span className="block text-xs capitalize text-slate-500">{user.role.replaceAll("_"," ")}</span></span><Link href="/" className="hidden text-sm text-slate-400 hover:text-white lg:block">View site ↗</Link><LogoutButton/></div></div></header><div className="mx-auto flex max-w-[1600px]"><aside className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-line bg-ink px-4 pt-5 transition-transform lg:sticky lg:top-16 lg:z-0 lg:h-[calc(100vh-4rem)] lg:w-64 lg:translate-x-0 lg:shrink-0 lg:overflow-y-auto lg:border-r lg:pt-6 ${open?'translate-x-0':'-translate-x-full'}`}><div className="mb-5 flex items-center justify-between px-2 lg:hidden"><span className="font-semibold">Navigation</span><button aria-label="Close navigation" onClick={()=>setOpen(false)}><X size={20}/></button></div><nav className="space-y-1">{links.map(([label, href])=>{const active=pathname===href||pathname.startsWith(`${href}/`);return <Link key={href} href={href} onClick={()=>setOpen(false)} className={`flex items-center justify-between rounded-xl px-3 py-2.5 text-sm transition ${active?'bg-primary/15 text-indigo-200':'text-slate-400 hover:bg-surface hover:text-white'}`}><span>{label}</span>{active&&<ChevronRight size={15}/>}</Link>})}</nav></aside>{open&&<button aria-label="Close navigation overlay" onClick={()=>setOpen(false)} className="fixed inset-0 z-40 bg-black/60 lg:hidden"/>}<main className="min-w-0 flex-1 px-4 py-7 lg:px-8">{children}</main></div></div>;
}

