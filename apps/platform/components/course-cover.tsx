import { BookOpen } from "lucide-react";

export function CourseCover({ src, title, className = "" }: { src?: string | null; title: string; className?: string }) {
  return <div className={`relative aspect-video overflow-hidden bg-gradient-to-br from-indigo-500/30 via-surface to-ink ${className}`}>
    {src ? <img src={src} alt={`${title} course cover`} className="h-full w-full object-cover" /> : <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-primary"><BookOpen size={28} aria-hidden="true" /><span className="text-xs font-semibold uppercase tracking-[.16em]">Learn-Coding</span></div>}
  </div>;
}
