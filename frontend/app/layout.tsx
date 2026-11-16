import type { Metadata } from "next";
import "./globals.css";
import { PwaRegister } from "@/components/pwa-register";
import { SiteFrame } from "@/components/site-frame";

export const metadata: Metadata = {
  title: { default: "Languages-Platform | Master Coding. Build Your Future.", template: "%s | Languages-Platform" },
  description: "Free programming courses, coding challenges, learning paths, and practical projects for curious builders.",
  openGraph: { title: "Languages-Platform", siteName: "Languages-Platform", description: "Master coding with free courses, challenges, and real-world projects.", type: "website" },
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en">
    <body><PwaRegister /><SiteFrame>{children}</SiteFrame></body>
  </html>;
}
