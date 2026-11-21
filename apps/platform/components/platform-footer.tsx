"use client";

import Image from "next/image";
import Link from "next/link";
import { Facebook, Github, Globe2, Linkedin, Mail, Youtube, type LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";

type FooterLink = { id: string; label: string; href: string; position: number; enabled: boolean };
type FooterGroup = { id: string; title: string; position: number; enabled: boolean; links: FooterLink[] };
type SocialLink = { id: string; platform: string; url: string; icon_key: string; position: number; enabled: boolean };
type FooterSettings = { tagline: string; description: string; groups: FooterGroup[]; social_links: SocialLink[]; newsletter_enabled: boolean; newsletter_note: string; copyright_text: string };
type Branding = { website_name: string; logo_url: string; footer_branding?: string; tagline?: string };

const fallbackFooter: FooterSettings = {
  tagline: "Learn to code. Build your future.",
  description: "Practical coding education, projects, and tools for your next step.",
  groups: [
    { id: "learn", title: "Learn", position: 0, enabled: true, links: [{ id: "courses", label: "Courses", href: "/courses", position: 0, enabled: true }, { id: "projects", label: "Projects", href: "/projects", position: 1, enabled: true }, { id: "challenges", label: "Challenges", href: "/challenges", position: 2, enabled: true }, { id: "paths", label: "Learning Paths", href: "/careers/paths", position: 3, enabled: true }] },
    { id: "careers", title: "Careers", position: 1, enabled: true, links: [{ id: "career-paths", label: "Career Paths", href: "/careers/paths", position: 0, enabled: true }, { id: "resume", label: "Resume Builder", href: "/careers/resume", position: 1, enabled: true }, { id: "interview", label: "Interview Preparation", href: "/careers/interview", position: 2, enabled: true }] },
    { id: "tools", title: "Tools", position: 2, enabled: true, links: [{ id: "tools", label: "Developer Tools", href: "/tools", position: 0, enabled: true }, { id: "json", label: "JSON Formatter", href: "/tools/json-formatter", position: 1, enabled: true }, { id: "regex", label: "Regex Tester", href: "/tools/regex-tester", position: 2, enabled: true }, { id: "playground", label: "Code Playground", href: "/tools/code-playground", position: 3, enabled: true }] },
    { id: "company", title: "Company", position: 3, enabled: true, links: [{ id: "about", label: "About", href: "/about", position: 0, enabled: true }, { id: "contact", label: "Contact", href: "/contact", position: 1, enabled: true }] },
    { id: "legal", title: "Legal", position: 4, enabled: true, links: [{ id: "privacy", label: "Privacy Policy", href: "/privacy", position: 0, enabled: true }, { id: "terms", label: "Terms of Service", href: "/terms", position: 1, enabled: true }] },
  ],
  social_links: [], newsletter_enabled: false, newsletter_note: "Newsletter sign-ups are not available yet.", copyright_text: "© 2026 Learn-Coding. All rights reserved.",
};

const socialIcons: Record<string, LucideIcon> = { github: Github, linkedin: Linkedin, youtube: Youtube, facebook: Facebook, globe: Globe2 };

function FooterLinkView({ link }: { link: FooterLink }) {
  return link.href.startsWith("/") ? <Link href={link.href} className="transition hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50">{link.label}</Link> : <a href={link.href} target="_blank" rel="noopener noreferrer" className="transition hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50">{link.label}</a>;
}

export function PlatformFooter() {
  const [footer, setFooter] = useState<FooterSettings>(fallbackFooter);
  const [branding, setBranding] = useState<Branding>({ website_name: "Learn-Coding", logo_url: "/branding/tkp.png" });

  useEffect(() => {
    Promise.all([fetch("/api/v1/site/footer"), fetch("/api/v1/site/branding")]).then(async ([footerResponse, brandingResponse]) => {
      if (footerResponse.ok) setFooter({ ...fallbackFooter, ...(await footerResponse.json()) });
      if (brandingResponse.ok) { const value = await brandingResponse.json(); setBranding(current => ({ ...current, ...value })); }
    }).catch(() => undefined);
  }, []);

  const groups = [...footer.groups].filter(group => group.enabled).sort((a, b) => a.position - b.position);
  const socialLinks = [...footer.social_links].filter(link => link.enabled).sort((a, b) => a.position - b.position);

  return <footer className="border-t border-line bg-surface text-sm text-muted" aria-labelledby="platform-footer-title">
    <div className="mx-auto max-w-6xl px-6 py-12 sm:py-16">
      {footer.newsletter_enabled && <section className="mb-12 flex flex-col gap-4 rounded-2xl border border-primary/20 bg-primary/10 p-6 sm:flex-row sm:items-center sm:justify-between" aria-labelledby="newsletter-title">
        <div className="flex items-start gap-3"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary/15 text-primary"><Mail size={19} aria-hidden="true" /></span><div><h2 id="newsletter-title" className="font-semibold text-foreground">Stay in the loop</h2><p className="mt-1 max-w-xl text-sm leading-6">{footer.newsletter_note}</p></div></div>
      </section>}
      <div className="grid gap-10 lg:grid-cols-[1.4fr_2fr]">
        <section aria-labelledby="platform-footer-title" className="max-w-sm">
          <div className="flex items-center gap-3"><Image src={branding.logo_url || "/branding/tkp.png"} alt="TKP logo" width={44} height={44} className="rounded-xl" /><div><h2 id="platform-footer-title" className="font-semibold text-foreground">{branding.website_name}</h2><p className="mt-1 text-xs text-muted">{branding.footer_branding || footer.tagline}</p></div></div>
          <p className="mt-5 leading-7">{footer.description}</p>
          {socialLinks.length > 0 && <div className="mt-6 flex items-center gap-2" aria-label="Social links">{socialLinks.map(link => { const Icon = socialIcons[link.icon_key] || Globe2; return <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" aria-label={`Learn-Coding on ${link.platform}`} className="grid h-9 w-9 place-items-center rounded-lg border border-line text-muted transition hover:border-primary hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"><Icon size={17} aria-hidden="true" /></a>; })}</div>}
        </section>
        <nav aria-label="Footer navigation" className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-5">{groups.map(group => <div key={group.id}><h3 className="text-xs font-semibold uppercase tracking-[.16em] text-foreground">{group.title}</h3><ul className="mt-4 space-y-3">{[...group.links].filter(link => link.enabled).sort((a, b) => a.position - b.position).map(link => <li key={link.id}><FooterLinkView link={link} /></li>)}</ul></div>)}</nav>
      </div>
      <div className="mt-12 flex flex-col gap-3 border-t border-line pt-6 text-xs sm:flex-row sm:items-center sm:justify-between"><p>{footer.copyright_text}</p><p>{footer.tagline}</p></div>
    </div>
  </footer>;
}
