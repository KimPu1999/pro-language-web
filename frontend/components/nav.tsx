"use client";

import Link from "next/link";
import Image from "next/image";
import { Menu, Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { routes } from "@/lib/routes";
import { LogoutButton } from "./auth-form";
import { LanguageSwitcher } from "./language-switcher";
import { useI18n } from "@/lib/i18n";

const links = [["home", routes.home], ["courses", routes.courses], ["projects", routes.projects], ["challenges", routes.challenges], ["careers", routes.careers], ["tools", routes.tools], ["about", routes.about], ["contact", routes.contact]] as const;

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

function navClass(active: boolean) {
  return `rounded-lg px-2 py-2 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${active ? "text-white" : "text-slate-300 hover:text-indigo-300"}`;
}

export function Nav() {
  const [open, setOpen] = useState(false);
  const [signedIn, setSignedIn] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const mobileMenuRef = useRef<HTMLElement>(null);
  const pathname = usePathname();
  const { t } = useI18n();
  const dashboardPage = pathname.startsWith("/dashboard") || pathname.startsWith("/my-learning");

  useEffect(() => { api.me().then(() => setSignedIn(true)).catch(() => setSignedIn(false)); }, []);
  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); };
    document.addEventListener("keydown", close);
    const previousOverflow = document.body.style.overflow;
    mobileMenuRef.current?.querySelector<HTMLElement>("a,button")?.focus();
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", close); document.body.style.overflow = previousOverflow; };
  }, [open]);
  useEffect(() => { setOpen(false); }, [pathname]);

  if (dashboardPage) return null;
  return <>
    <header className="site-nav fixed inset-x-0 top-0 z-50 w-full isolate border-b border-line/70 bg-ink/95 shadow-lg shadow-black/10 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-5 lg:px-8">
        <Link href="/" aria-label="Languages-Platform home" className="flex shrink-0 items-center gap-2 font-bold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">
          <Image src="/branding/tkp.png" alt="Languages-Platform logo" width={40} height={40} className="h-10 w-10 object-contain" priority />
          <span className="hidden sm:inline">Languages-Platform</span>
        </Link>
        <nav aria-label="Primary navigation" className="hidden items-center gap-1 xl:flex">
          {links.map(([key, href]) => { const active = isActive(pathname, href); return <Link key={href} href={href} aria-current={active ? "page" : undefined} className={navClass(active)}>{t(key)}</Link>; })}
        </nav>
        <div className="ml-auto flex items-center gap-1 xl:ml-0">
          <Link aria-label={t("search")} href="/courses" className="rounded-lg p-2 text-slate-300 transition hover:bg-surface hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"><Search size={17}/></Link>
          <LanguageSwitcher />
          <div className="hidden items-center gap-1 xl:flex">{signedIn ? <><Link aria-current={isActive(pathname, "/dashboard") ? "page" : undefined} className={navClass(isActive(pathname, "/dashboard"))} href="/dashboard">Dashboard</Link><Link aria-current={isActive(pathname, "/profile") ? "page" : undefined} className={navClass(isActive(pathname, "/profile"))} href="/profile">Profile</Link><LogoutButton /></> : <><Link className={navClass(false)} href="/login">Log in</Link><Link className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400" href="/register">Join free</Link></>}</div>
          <button ref={menuButtonRef} type="button" aria-label={open ? "Close navigation menu" : "Open navigation menu"} aria-expanded={open} aria-controls="mobile-primary-navigation" onClick={() => setOpen(value => !value)} className="rounded-lg p-2 text-slate-200 transition hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 xl:hidden">{open ? <X size={21}/> : <Menu size={21}/>}</button>
        </div>
      </div>
      {open && <nav ref={mobileMenuRef} id="mobile-primary-navigation" aria-label="Mobile primary navigation" className="relative z-50 max-h-[calc(100dvh-4rem)] overflow-y-auto overscroll-contain border-t border-line bg-ink px-5 pb-[calc(1rem+env(safe-area-inset-bottom))] xl:hidden"><div className="flex items-center justify-between border-b border-line/50 py-3"><span className="text-sm text-slate-400">{t("language")}</span><LanguageSwitcher /></div>{links.map(([key, href]) => { const active = isActive(pathname, href); return <Link href={href} aria-current={active ? "page" : undefined} className={`${navClass(active)} my-1 block border-b border-line/50 py-3`} key={href}>{t(key)}</Link>; })}<Link href="/courses" className={`${navClass(isActive(pathname, "/courses"))} flex items-center gap-2 border-b border-line/50 py-3`}><Search size={16}/> {t("search")}</Link>{signedIn ? <><Link className={`${navClass(isActive(pathname, "/dashboard"))} block py-3`} href="/dashboard">{t("dashboard")}</Link><Link className={`${navClass(isActive(pathname, "/profile"))} block py-3`} href="/profile">{t("profile")}</Link><div className="py-2"><LogoutButton /></div></> : <><Link className={`${navClass(false)} block py-3`} href="/login">{t("login")}</Link><Link className="block rounded-lg bg-primary px-3 py-2 text-center text-sm font-semibold text-white" href="/register">{t("joinFree")}</Link></>}</nav>}
    </header>
    {signedIn && <nav aria-label="Mobile learning navigation" className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-4 border-t border-line bg-ink/95 p-2 pb-[calc(.5rem+env(safe-area-inset-bottom))] text-center text-[11px] backdrop-blur xl:hidden"><Link className="rounded-lg p-2 text-slate-300" href="/dashboard">Learn</Link><Link className="rounded-lg p-2 text-slate-300" href="/offline/library">Library</Link><Link className="rounded-lg p-2 text-slate-300" href="/offline/downloads">Sync</Link><Link className="rounded-lg p-2 text-slate-300" href="/settings/notifications">Settings</Link></nav>}
  </>;
}
