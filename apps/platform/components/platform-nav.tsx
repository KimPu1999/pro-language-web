"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BriefcaseBusiness, BookOpen, ChevronRight, Code2, FolderCode, House, LogIn, Menu, UserRound, Wrench, X, type LucideIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { ThemeSwitcher } from "@/components/theme-provider";

const fallbackLinks = [["Courses", "/courses"], ["Projects", "/projects"], ["Challenges", "/challenges"], ["Careers", "/careers"], ["Developer Tools", "/tools"]] as const;
type PublicLink = { label: string; href: string; enabled: boolean; position: number; area: "header" | "footer" };
type Branding = { website_name: string; logo_url: string };
type AuthUser = { full_name: string; email: string; role: string };

const iconByRoute: Record<string, LucideIcon> = {
  "/": House,
  "/courses": BookOpen,
  "/projects": FolderCode,
  "/challenges": Code2,
  "/careers": BriefcaseBusiness,
  "/tools": Wrench,
};

const csrf = () => document.cookie.match(/(?:^|; )cm_csrf=([^;]+)/)?.[1] ?? "";

function isActiveRoute(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

export function PlatformNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [links, setLinks] = useState<readonly (readonly [string, string])[]>(fallbackLinks);
  const [branding, setBranding] = useState<Branding>({ website_name: "Learn-Coding", logo_url: "/branding/tkp.png" });
  const [user, setUser] = useState<AuthUser | null>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const menuPanelRef = useRef<HTMLElement>(null);
  const firstMenuLinkRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    Promise.all([fetch("/api/v1/site/branding"), fetch("/api/v1/site/navigation"), fetch("/api/v1/auth/me", { credentials: "include" })]).then(async ([brandingResponse, navigationResponse, userResponse]) => {
      if (brandingResponse.ok) {
        const value = await brandingResponse.json();
        setBranding({ website_name: value.website_name || "Learn-Coding", logo_url: value.logo_url || "/branding/tkp.png" });
      }
      if (navigationResponse.ok) {
        const value = await navigationResponse.json();
        const headerLinks = (value.items as PublicLink[] | undefined)?.filter(item => item.enabled && item.area === "header").sort((a, b) => a.position - b.position).map(item => [item.label, item.href] as [string, string]);
        if (headerLinks?.length) setLinks(headerLinks);
      }
      if (userResponse.ok) setUser(await userResponse.json());
    }).catch(() => undefined);
  }, []);

  const navigationLinks = useMemo(() => [{ label: "Home", href: "/" }, ...links.filter(([, href]) => href !== "/").map(([label, href]) => ({ label, href }))], [links]);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        menuButtonRef.current?.focus();
      }
    };
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!menuPanelRef.current?.contains(target) && !menuButtonRef.current?.contains(target)) setOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onPointerDown);
    const frame = window.requestAnimationFrame(() => firstMenuLinkRef.current?.focus());
    return () => { document.removeEventListener("keydown", onKeyDown); document.removeEventListener("pointerdown", onPointerDown); window.cancelAnimationFrame(frame); };
  }, [open]);

  async function signOut() {
    const response = await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include", headers: { "X-CSRF-Token": csrf() } });
    if (response.ok) {
      setUser(null);
      setOpen(false);
      router.push("/");
      router.refresh();
    }
  }

  function closeMenu() {
    setOpen(false);
  }

  function iconForRoute(href: string) {
    return iconByRoute[href] || Wrench;
  }

  return <header className="sticky top-0 z-40 shrink-0 border-b border-line bg-surface/95 shadow-sm backdrop-blur">
    <div className="mx-auto flex min-h-16 max-w-6xl items-center gap-4 px-4 sm:px-6">
      <Link href="/" className="flex min-w-0 shrink-0 items-center gap-2 font-bold" onClick={closeMenu} aria-label={`${branding.website_name} home`}>
        <Image src={branding.logo_url} alt={`${branding.website_name} logo`} width={36} height={36} className="rounded-xl" />
        <span className="truncate">{branding.website_name}</span>
      </Link>

      <div className="ml-auto flex items-center gap-2 lg:hidden">
        <ThemeSwitcher />
        <button ref={menuButtonRef} type="button" aria-label={open ? "Close navigation menu" : "Open navigation menu"} aria-expanded={open} aria-controls="platform-mobile-navigation" className="grid h-9 w-9 place-items-center rounded-lg border border-line bg-surface text-muted transition hover:bg-surface-hover hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40" onClick={() => setOpen(value => !value)}>
          {open ? <X size={19} aria-hidden="true" /> : <Menu size={19} aria-hidden="true" />}
        </button>
      </div>

      <nav aria-label="Public navigation" className="ml-auto hidden items-center gap-2 lg:flex">
        {navigationLinks.map(({ label, href }) => { const active = isActiveRoute(pathname, href); return <Link key={`${href}-${label}`} href={href} onClick={closeMenu} aria-current={active ? "page" : undefined} className={`rounded-lg px-3 py-2 text-sm transition ${active ? "bg-primary/10 font-medium text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}>{label}</Link>; })}
        <ThemeSwitcher />
        {user ? <div className="flex items-center gap-2"><Link href="/profile" onClick={closeMenu} className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><UserRound size={16} aria-hidden="true" /> Profile</Link><button type="button" onClick={signOut} className="rounded-lg border border-line px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground">Sign out</button></div> : <Link href="/login" onClick={closeMenu} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-center text-sm font-semibold text-white transition hover:bg-primary-hover"><LogIn size={16} aria-hidden="true" /> Sign in</Link>}
      </nav>
    </div>

    {open && <nav ref={menuPanelRef} id="platform-mobile-navigation" aria-label="Mobile public navigation" className="absolute inset-x-0 top-full border-b border-line bg-surface shadow-lg lg:hidden">
      <div className="mx-auto max-h-[calc(100dvh-4rem)] max-w-6xl overflow-y-auto overscroll-contain px-4 py-3 sm:px-6">
        <div className="space-y-1 rounded-2xl border border-line bg-surface-elevated/50 p-2">
          {navigationLinks.map(({ label, href }, index) => { const Icon = iconForRoute(href); const active = isActiveRoute(pathname, href); return <Link key={`${href}-${label}`} ref={index === 0 ? firstMenuLinkRef : undefined} href={href} onClick={closeMenu} aria-current={active ? "page" : undefined} className={`flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${active ? "bg-primary/12 font-semibold text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`}><Icon size={18} aria-hidden="true" /><span className="flex-1">{label}</span><ChevronRight size={16} aria-hidden="true" /></Link>; })}
          <div className="my-2 border-t border-line" />
          {user ? <><Link href="/profile" onClick={closeMenu} className="flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><UserRound size={18} aria-hidden="true" /><span className="flex-1">Profile</span><ChevronRight size={16} aria-hidden="true" /></Link><button type="button" onClick={signOut} className="flex min-h-12 w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><LogIn size={18} aria-hidden="true" /><span className="flex-1">Sign out</span></button></> : <Link href="/login" onClick={closeMenu} className="flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-primary transition hover:bg-surface-hover"><LogIn size={18} aria-hidden="true" /><span className="flex-1">Sign in</span><ChevronRight size={16} aria-hidden="true" /></Link>}
        </div>
      </div>
    </nav>}
  </header>;
}
