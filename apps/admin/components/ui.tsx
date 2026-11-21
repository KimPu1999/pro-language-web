import { ReactNode } from "react";

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) {
  return <div className="flex flex-col gap-5 border-b border-line pb-7 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">{eyebrow || "Admin workspace"}</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{title}</h1>{description && <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>}</div>{actions && <div className="flex shrink-0 flex-wrap gap-3">{actions}</div>}</div>;
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-line bg-surface shadow-panel ${className}`}>{children}</section>;
}

export function Button({ children, variant = "primary", className = "", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "quiet" | "danger" }) {
  const styles = { primary: "bg-primary text-white shadow-lg shadow-indigo-950/20 hover:bg-indigo-500", secondary: "border border-line bg-white/[.03] text-slate-200 hover:bg-white/[.07]", quiet: "text-muted hover:bg-white/[.06] hover:text-white", danger: "border border-red-400/20 bg-red-500/10 text-red-200 hover:bg-red-500/20" };
  return <button {...props} className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}>{children}</button>;
}

export function StatusBadge({ value, tone }: { value: string; tone?: "success" | "warning" | "danger" | "neutral" }) {
  const normalized = tone || (value.toLowerCase().includes("publish") || value.toLowerCase() === "active" ? "success" : value.toLowerCase().includes("draft") || value.toLowerCase().includes("review") ? "warning" : "neutral");
  const styles = { success: "border-emerald-400/20 bg-emerald-400/10 text-emerald-200", warning: "border-amber-400/20 bg-amber-400/10 text-amber-200", danger: "border-red-400/20 bg-red-400/10 text-red-200", neutral: "border-line bg-white/[.04] text-muted" };
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${styles[normalized]}`}>{value.replaceAll("_", " ")}</span>;
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="rounded-2xl border border-dashed border-line px-6 py-14 text-center"><p className="font-medium text-slate-200">{title}</p><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">{description}</p></div>;
}

export function LoadingRows({ columns = 4 }: { columns?: number }) {
  return <div className="space-y-3 p-5" aria-label="Loading"><span className="sr-only">Loading</span>{Array.from({ length: 5 }).map((_, row) => <div key={row} className="grid gap-4 sm:grid-cols-4">{Array.from({ length: columns }).map((__, column) => <div key={column} className="h-10 animate-pulse rounded-lg bg-white/[.05]" />)}</div>)}</div>;
}

export function Breadcrumbs({ items }: { items: { label: string; href?: string }[] }) {
  return <nav aria-label="Breadcrumb" className="mb-5 flex flex-wrap items-center gap-2 text-xs text-muted">{items.map((item, index) => <span key={`${item.label}-${index}`} className="flex items-center gap-2">{index > 0 && <span className="text-slate-600">/</span>}{item.href ? <a className="hover:text-white" href={item.href}>{item.label}</a> : <span className="text-slate-300">{item.label}</span>}</span>)}</nav>;
}
