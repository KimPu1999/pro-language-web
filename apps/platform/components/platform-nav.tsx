"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BriefcaseBusiness, BookOpen, ChevronDown, ChevronRight, Code2, FolderCode, House, LogIn, Menu, UserRound, Wrench, X, type LucideIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type Ref } from "react";
import { ThemeSwitcher } from "@/components/theme-provider";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useI18n } from "@/lib/i18n";

const fallbackLinks = [{ id: "courses", label: "Courses", href: "/courses", enabled: true, position: 0, area: "header" as const, link_type: "internal" as const }, { id: "projects", label: "Projects", href: "/projects", enabled: true, position: 1, area: "header" as const, link_type: "internal" as const }, { id: "challenges", label: "Challenges", href: "/challenges", enabled: true, position: 2, area: "header" as const, link_type: "internal" as const }, { id: "careers", label: "Careers", href: "/careers", enabled: true, position: 3, area: "header" as const, link_type: "internal" as const }, { id: "tools", label: "Developer Tools", href: "/tools", enabled: true, position: 4, area: "header" as const, link_type: "internal" as const }];
const requiredPublicLinks: PublicLink[] = [{ id: "about", label: "About", href: "/about", enabled: true, position: 90, area: "header", link_type: "internal", parent_id: null }, { id: "contact", label: "Contact", href: "/contact", enabled: true, position: 91, area: "header", link_type: "internal", parent_id: null }];
type PublicLink = { id: string; label: string; href: string; enabled: boolean; position: number; area: "header" | "footer"; link_type?: "internal" | "external"; external_url?: string | null; parent_id?: string | null; target_blank?: boolean };
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
  const { t } = useI18n();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [links, setLinks] = useState<PublicLink[]>(fallbackLinks);
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
        const headerLinks = (value.items as PublicLink[] | undefined)?.filter(item => item.enabled && item.area === "header").sort((a, b) => a.position - b.position);
        if (headerLinks?.length) setLinks(headerLinks);
      }
      if (userResponse.ok) setUser(await userResponse.json());
    }).catch(() => undefined);
  }, []);

  const navigationLinks = useMemo(() => { const existing = new Set(links.map(link => link.href)); const merged = [...links, ...requiredPublicLinks.filter(link => !existing.has(link.href))]; return [{ id: "home", label: "Home", href: "/", enabled: true, position: -1, area: "header" as const, link_type: "internal" as const }, ...merged.filter(link => link.href !== "/" && !link.parent_id).sort((a, b) => a.position - b.position)]; }, [links]);

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

  function destination(link: PublicLink) { return link.link_type === "external" ? (link.external_url || link.href) : link.href; }
  function labelFor(label: string) { const key = ({ Home: "home", Courses: "courses", Projects: "projects", Challenges: "challenges", Careers: "careers", Tools: "tools", "Developer Tools": "tools", About: "about", Contact: "contact" } as Record<string, string>)[label]; return key ? t(key) : label; }

  function linkView(link: PublicLink, className: string, child = false, Icon?: LucideIcon, active = false, ref?: Ref<HTMLAnchorElement>) {
    const href = destination(link); const props = { className, target: link.target_blank ? "_blank" : undefined, rel: link.target_blank ? "noopener noreferrer" : undefined, onClick: closeMenu, "aria-current": active ? "page" as const : undefined, ref };
    return href.startsWith("/") ? <Link href={href} {...props}>{Icon ? <Icon size={18} aria-hidden="true" /> : child && <ChevronRight size={15} aria-hidden="true" />}<span className="flex-1">{labelFor(link.label)}</span></Link> : <a href={href} {...props}>{Icon ? <Icon size={18} aria-hidden="true" /> : child && <ChevronRight size={15} aria-hidden="true" />}<span className="flex-1">{labelFor(link.label)}</span></a>;
  }

  return <header className="sticky top-0 z-[70] shrink-0 border-b border-line bg-surface/95 shadow-sm backdrop-blur">
    <div className="mx-auto flex min-h-16 w-full min-w-0 max-w-6xl items-center gap-3 px-4 sm:gap-4 sm:px-6">
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

      <nav aria-label="Public navigation" className="ml-auto hidden items-center gap-1.5 lg:flex">
        {navigationLinks.map(link => { const href = destination(link); const active = isActiveRoute(pathname, href); const children = links.filter(child => child.parent_id === link.id && child.enabled).sort((a, b) => a.position - b.position); return children.length ? <div key={link.id} className="group relative"><button type="button" className={`inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm transition ${active ? "bg-primary/10 font-medium text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`} aria-haspopup="menu">{link.label}<ChevronDown size={14} aria-hidden="true" /></button><div className="invisible absolute left-0 top-full z-10 min-w-48 translate-y-1 rounded-xl border border-line bg-surface p-1 opacity-0 shadow-xl transition group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100">{children.map(child => <span key={child.id}>{linkView(child, `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${isActiveRoute(pathname, destination(child)) ? "bg-primary/10 text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`, true, undefined, isActiveRoute(pathname, destination(child)))}</span>)}</div></div> : linkView(link, `rounded-lg px-3 py-2 text-sm transition ${active ? "bg-primary/10 font-medium text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`, false, undefined, active); })}
        <ThemeSwitcher /><LanguageSwitcher />
        {user ? <div className="flex items-center gap-2"><Link href="/profile" onClick={closeMenu} className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><UserRound size={16} aria-hidden="true" /> {t("profile")}</Link><button type="button" onClick={signOut} className="rounded-lg border border-line px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground">{t("signOut")}</button></div> : <Link href="/login" onClick={closeMenu} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-center text-sm font-semibold text-white transition hover:bg-primary-hover"><LogIn size={16} aria-hidden="true" /> {t("signIn")}</Link>}
      </nav>
    </div>

    {open && <nav ref={menuPanelRef} id="platform-mobile-navigation" aria-label="Mobile public navigation" className="absolute inset-x-0 top-full z-[80] border-b border-line bg-surface shadow-lg lg:hidden">
      <div className="mx-auto max-h-[calc(100dvh-4rem)] max-w-6xl overflow-y-auto overscroll-contain px-4 py-3 sm:px-6">
        <div className="space-y-1 rounded-2xl border border-line bg-surface-elevated/50 p-2">
          {navigationLinks.map((link, index) => { const Icon = iconForRoute(destination(link)); const active = isActiveRoute(pathname, destination(link)); const children = links.filter(child => child.parent_id === link.id && child.enabled).sort((a, b) => a.position - b.position); return <div key={link.id}>{linkView(link, `flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${active ? "bg-primary/12 font-semibold text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`, false, Icon, active, index === 0 ? firstMenuLinkRef : undefined)}{children.map(child => <span key={child.id}>{linkView(child, `ml-8 flex min-h-11 items-center gap-2 rounded-xl px-3 py-2 text-sm transition ${isActiveRoute(pathname, destination(child)) ? "bg-primary/10 font-semibold text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"}`, true, undefined, isActiveRoute(pathname, destination(child)))}</span>)}</div>; })}
          <div className="my-2 border-t border-line" />
          <div className="flex items-center justify-between border-t border-line px-3 py-3"><span className="text-sm text-muted">{t("language")}</span><LanguageSwitcher /></div>{user ? <><Link href="/profile" onClick={closeMenu} className="flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><UserRound size={18} aria-hidden="true" /><span className="flex-1">{t("profile")}</span><ChevronRight size={16} aria-hidden="true" /></Link><button type="button" onClick={signOut} className="flex min-h-12 w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-muted transition hover:bg-surface-hover hover:text-foreground"><LogIn size={18} aria-hidden="true" /><span className="flex-1">{t("signOut")}</span></button></> : <Link href="/login" onClick={closeMenu} className="flex min-h-12 items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-primary transition hover:bg-surface-hover"><LogIn size={18} aria-hidden="true" /><span className="flex-1">{t("signIn")}</span><ChevronRight size={16} aria-hidden="true" /></Link>}
        </div>
      </div>
    </nav>}
  </header>;
}
