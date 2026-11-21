"use client";

import { usePathname } from "next/navigation";
import { PlatformFooter } from "@/components/platform-footer";
import { PlatformNav } from "@/components/platform-nav";

export function PlatformShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLessonPage = pathname.startsWith("/courses/") && pathname.includes("/learn/");

  return <div className={`${isLessonPage ? "flex h-dvh flex-col overflow-hidden" : "flex min-h-dvh flex-col"} min-w-0`}>
    <a href="#platform-main" className="sr-only z-[100] rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white focus:not-sr-only focus:fixed focus:left-4 focus:top-4">Skip to content</a>
    <PlatformNav />
    <main id="platform-main" className={`${isLessonPage ? "flex min-h-0 flex-1 flex-col" : "flex-1"} min-w-0`}>{children}</main>
    {!isLessonPage && <PlatformFooter />}
  </div>;
}
