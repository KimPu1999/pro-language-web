"use client";

import Link from "next/link";
import { CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";
import { use, useEffect, useState } from "react";

type Result = { status: string; award_id: string; title?: string; issuer?: string; awarded_at?: string; criteria_version?: number };

export default function VerifyAchievement({ params }: { params: Promise<{ publicId: string }> }) {
  const { publicId } = use(params); const [data, setData] = useState<Result | null>(null); const [loading, setLoading] = useState(true);
  useEffect(() => { fetch(`/api/v1/achievements/verify/${encodeURIComponent(publicId)}`, { cache: "no-store" }).then(response => response.json()).then(value => setData(value)).catch(() => setData({ status: "error", award_id: publicId })).finally(() => setLoading(false)); }, [publicId]);
  if (loading) return <section className="mx-auto max-w-2xl px-5 py-14 text-sm text-muted">Checking verified achievement…</section>;
  const valid = data?.status === "valid"; const revoked = data?.status === "revoked";
  return <section className="mx-auto max-w-2xl px-5 py-12 sm:px-6 sm:py-16"><div className="rounded-3xl border border-line bg-surface p-7 text-center sm:p-10">{valid ? <CheckCircle2 className="mx-auto text-emerald-500" size={46} /> : <ShieldAlert className="mx-auto text-amber-500" size={46} />}<p className="mt-5 text-xs font-semibold uppercase tracking-[.18em] text-primary">Learn-Coding verification</p><h1 className="mt-3 text-2xl font-bold">{valid ? "Verified achievement" : revoked ? "Revoked achievement" : "Achievement not found"}</h1>{data?.title && <p className="mt-4 text-lg font-semibold">{data.title}</p>}{valid && <div className="mt-6 space-y-2 text-sm text-muted"><p>Issued by {data.issuer}</p><p>Awarded {data.awarded_at ? new Date(data.awarded_at).toLocaleDateString() : "—"}</p><p>Criteria version {data.criteria_version ?? "—"}</p></div>}<p className="mt-6 break-all font-mono text-xs text-muted">Award ID: {data?.award_id || publicId}</p><Link href="/achievements" className="mt-7 inline-flex items-center gap-2 text-sm font-semibold text-primary"><ShieldCheck size={16} /> View achievements</Link></div></section>;
}
