"use client";

import { useEffect, useState } from "react";

type Asset = { id: string; title: string; url: string; mime_type: string; alt_text: string };
type Props = { value?: string | null; onSelect: (asset: Asset) => void; label?: string };

export function MediaPicker({ value, onSelect, label = "Choose from Media Library" }: Props) {
  const [open, setOpen] = useState(false); const [items, setItems] = useState<Asset[]>([]); const [search, setSearch] = useState("");
  useEffect(() => { if (!open) return; const params = new URLSearchParams({ page_size: "24" }); if (search) params.set("search", search); fetch(`/api/v1/admin/media?${params}`, { credentials: "include" }).then(response => response.ok ? response.json() : null).then(value => setItems(value?.items ?? [])).catch(() => setItems([])); }, [open, search]);
  return <div><button type="button" onClick={() => setOpen(true)} className="rounded-xl border border-line px-3 py-2 text-sm text-muted hover:bg-surface-hover">{label}</button>{value && <span className="ml-2 text-xs text-muted">Selected</span>}{open && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/60 p-4"><div className="max-h-[80dvh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-line bg-surface p-5"><div className="flex items-center justify-between gap-4"><h2 className="font-semibold">Select media</h2><button type="button" onClick={() => setOpen(false)} className="text-sm text-muted">Close</button></div><input autoFocus value={search} onChange={event => setSearch(event.target.value)} placeholder="Search media" className="mt-4 h-10 w-full rounded-xl border border-line bg-ink px-3 text-sm" />{items.length ? <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">{items.map(item => <button type="button" key={item.id} onClick={() => { onSelect(item); setOpen(false); }} className="rounded-xl border border-line p-2 text-left hover:border-primary">{item.mime_type.startsWith("image/") ? <img src={item.url} alt={item.alt_text || item.title} className="aspect-video w-full rounded-lg object-cover" /> : <div className="aspect-video rounded-lg bg-red-500/10" />}<p className="mt-2 truncate text-xs">{item.title}</p></button>)}</div> : <p className="mt-6 text-sm text-muted">No media assets found.</p>}</div></div>}</div>;
}
