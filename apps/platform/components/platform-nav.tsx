"use client";

import Image from "next/image";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ThemeSwitcher } from "@/components/theme-provider";

const fallbackLinks = [["Courses", "/courses"], ["Projects", "/projects"], ["Challenges", "/challenges"], ["Careers", "/careers"], ["Developer Tools", "/tools"]] as const;
type PublicLink = { label: string; href: string; enabled: boolean; position: number; area: "header" | "footer" };
type Branding = { website_name: string; logo_url: string };

export function PlatformNav() {
  const [open, setOpen] = useState(false);
  const [links, setLinks] = useState<readonly (readonly [string, string])[]>(fallbackLinks);
  const [branding, setBranding] = useState<Branding>({ website_name: "Learn-Coding", logo_url: "/branding/tkp.png" });

  useEffect(() => {
    Promise.all([fetch("/api/v1/site/branding"), fetch("/api/v1/site/navigation")]).then(async ([brandingResponse, navigationResponse]) => {
      if (brandingResponse.ok) {
        const value = await brandingResponse.json();
        setBranding({ website_name: value.website_name || "Learn-Coding", logo_url: value.logo_url || "/branding/tkp.png" });
      }
      if (navigationResponse.ok) {
        const value = await navigationResponse.json();
        const headerLinks = (value.items as PublicLink[] | undefined)?.filter(item => item.enabled && item.area === "header").sort((a, b) => a.position - b.position).map(item => [item.label, item.href] as [string, string]);
        if (headerLinks?.length) setLinks(headerLinks);
      }
    }).catch(() => undefined);
  }, []);

  return <header className="sticky top-0 z-20 border-b border-line bg-surface/95 shadow-sm backdrop-blur">
    <div className="mx-auto flex min-h-16 max-w-6xl items-center gap-5 px-4 sm:px-6">
      <Link href="/" className="flex shrink-0 items-center gap-2 font-bold" onClick={() => setOpen(false)} aria-label={`${branding.website_name} home`}>
        <Image src={branding.logo_url} alt={`${branding.website_name} logo`} width={36} height={36} className="rounded-xl" />
        <span>{branding.website_name}</span>
      </Link>
      <button type="button" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} className="ml-auto rounded-lg border border-line bg-surface p-2 text-muted transition hover:bg-surface-hover hover:text-foreground md:hidden" onClick={() => setOpen(value => !value)}>
        {open ? <X size={19} /> : <Menu size={19} />}
      </button>
      <nav aria-label="Public navigation" className={`${open ? "flex" : "hidden"} absolute left-0 right-0 top-16 flex-col gap-1 border-b border-line bg-surface p-4 shadow-lg md:static md:ml-auto md:flex md:flex-row md:items-center md:gap-2 md:border-0 md:bg-transparent md:p-0 md:shadow-none`}>
        <Link href="/" onClick={() => setOpen(false)} className="rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground">Home</Link>
        {links.map(([label, href]) => <Link key={href} href={href} onClick={() => setOpen(false)} className="rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-hover hover:text-foreground">{label}</Link>)}
        <ThemeSwitcher />
        <Link href="/login" onClick={() => setOpen(false)} className="rounded-lg bg-primary px-4 py-2 text-center text-sm font-semibold text-white transition hover:bg-primary-hover">Sign in</Link>
      </nav>
    </div>
  </header>;
}
