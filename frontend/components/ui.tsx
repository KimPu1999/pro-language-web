import { cn } from "./utils";
export function Button({ className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) { return <button className={cn("rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50", className)} {...props} />; }
export function Badge({ children, className }: { children: React.ReactNode; className?: string }) { return <span className={cn("rounded-full bg-indigo-500/15 px-2.5 py-1 text-xs font-semibold text-indigo-300", className)}>{children}</span>; }
export function Card({ children, className }: { children: React.ReactNode; className?: string }) { return <div className={cn("rounded-2xl border border-line bg-surface", className)}>{children}</div>; }
export function Skeleton({ className }: { className?: string }) { return <div className={cn("animate-pulse rounded-lg bg-elevated", className)} />; }
