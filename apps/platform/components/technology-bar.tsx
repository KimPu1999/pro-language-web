"use client";
import { ChevronLeft, ChevronRight, Code2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
export type Technology = { name: string; slug: string; color?: string; icon?: string | null; published_course_count?: number };
export function TechnologyBar({ technologies, active, onSelect, onUnavailable = name => window.alert(`No published course is currently available for ${name}.`) }: { technologies: Technology[]; active: string; onSelect: (slug: string) => void; onUnavailable?: (name: string) => void }) {
  const router = useRouter();
  const scroller = useRef<HTMLDivElement>(null); const [canLeft, setCanLeft] = useState(false); const [canRight, setCanRight] = useState(false);
  function updateArrows() { const node = scroller.current; if (!node) return; setCanLeft(node.scrollLeft > 4); setCanRight(node.scrollLeft + node.clientWidth < node.scrollWidth - 4); }
  useEffect(() => { updateArrows(); const node = scroller.current; if (!node) return; node.addEventListener("scroll", updateArrows, { passive: true }); window.addEventListener("resize", updateArrows); return () => { node.removeEventListener("scroll", updateArrows); window.removeEventListener("resize", updateArrows); }; }, [technologies]);
  function move(direction: number) { scroller.current?.scrollBy({ left: direction * 280, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); }
  function select(item: Technology | null) {
    if (!item) { onSelect(""); return; }
    if (item.published_course_count === 0) { onUnavailable?.(item.name); return; }
    if (item.published_course_count !== 1) { onSelect(item.slug); return; }
    fetch(`/api/v1/courses?technology=${encodeURIComponent(item.slug)}&page=1&page_size=2&sort=title_asc`).then(response => response.ok ? response.json() : Promise.reject(new Error("course lookup failed"))).then((result: { total: number; items: { slug: string }[] }) => {
      if (result.total === 1 && result.items[0]?.slug) router.push(`/courses/${result.items[0].slug}`);
      else if (result.total > 1) onSelect(item.slug);
      else onUnavailable?.(item.name);
    }).catch(() => onUnavailable?.(item.name));
  }
  return <section aria-label="Browse courses by technology" className="sticky top-16 z-50 h-11 border-y border-line bg-surface/95 backdrop-blur"><div className="mx-auto flex h-full max-w-7xl items-center gap-1.5 px-3 sm:px-6"><button type="button" aria-label="Scroll technologies left" disabled={!canLeft} onClick={() => move(-1)} className="hidden h-7 w-7 shrink-0 place-items-center rounded-md border border-line text-muted transition hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-30 sm:grid"><ChevronLeft size={14}/></button><div ref={scroller} tabIndex={0} onKeyDown={event => { if (event.key === "ArrowRight") move(1); if (event.key === "ArrowLeft") move(-1); }} className="scrollbar-hidden flex min-w-0 flex-1 gap-1.5 overflow-x-auto py-1.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary" role="tablist" aria-label="Course technologies"><button type="button" role="tab" aria-selected={!active} onClick={() => select(null)} className={`inline-flex h-7 shrink-0 items-center gap-1.5 rounded-md border px-2.5 text-[11px] font-medium transition ${!active ? "border-primary bg-primary/10 text-primary" : "border-line bg-surface text-muted hover:border-primary/60 hover:text-foreground"}`}><Code2 size={14}/>All</button>{technologies.map(item => <button key={item.slug} type="button" role="tab" aria-selected={active === item.slug} onClick={() => select(item)} className={`inline-flex h-7 shrink-0 items-center gap-1.5 rounded-md border px-2.5 text-[11px] font-medium transition ${active === item.slug ? "border-primary bg-primary/10 text-primary" : "border-line bg-surface text-muted hover:border-primary/60 hover:text-foreground"}`}><span className="grid h-4 w-4 place-items-center rounded-full text-[9px] font-bold text-white" style={{ backgroundColor: item.color || "#6366F1" }}>{item.name.slice(0, 1).toUpperCase()}</span>{item.name}</button>)}</div><button type="button" aria-label="Scroll technologies right" disabled={!canRight} onClick={() => move(1)} className="hidden h-7 w-7 shrink-0 place-items-center rounded-md border border-line text-muted transition hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-30 sm:grid"><ChevronRight size={14}/></button></div></section>;
}
