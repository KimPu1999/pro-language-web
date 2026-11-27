import type { Metadata } from "next";
import "./globals.css";
import { PwaRegister } from "@/components/pwa-register";
import { SiteFrame } from "@/components/site-frame";
import { I18nProvider } from "@/lib/i18n";

const fallbackMetadata: Metadata = {
  title: { default: "Learn-Coding | Master Coding. Build Your Future.", template: "%s | Learn-Coding" },
  description: "Free programming courses, coding challenges, learning paths, and practical projects for curious builders.",
  openGraph: { title: "Learn-Coding", siteName: "Learn-Coding", description: "Master coding with free courses, challenges, and real-world projects.", type: "website" },
};

export async function generateMetadata(): Promise<Metadata> {
  const base = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${base}/api/v1/public/platform-config`, { cache: "no-store" });
    if (!response.ok) return fallbackMetadata;
    const config = await response.json() as { website: { name: string; site_url: string }; seo: { default_title: string; meta_description: string; open_graph_title: string; open_graph_description: string; open_graph_image: string | null; canonical_url: string; robots_indexing: boolean } };
    return {
      metadataBase: new URL(config.website.site_url),
      title: { default: config.seo.default_title || config.website.name, template: `%s | ${config.website.name}` },
      description: config.seo.meta_description,
      openGraph: { title: config.seo.open_graph_title || config.seo.default_title, siteName: config.website.name, description: config.seo.open_graph_description || config.seo.meta_description, type: "website", images: config.seo.open_graph_image ? [config.seo.open_graph_image] : undefined },
      alternates: { canonical: config.seo.canonical_url },
      robots: config.seo.robots_indexing ? { index: true, follow: true } : { index: false, follow: false },
    };
  } catch {
    return fallbackMetadata;
  }
}

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" suppressHydrationWarning>
    <body><I18nProvider><PwaRegister /><SiteFrame>{children}</SiteFrame></I18nProvider></body>
  </html>;
}
