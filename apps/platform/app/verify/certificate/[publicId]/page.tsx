"use client";

import Link from "next/link";
import { CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";
import { use, useEffect, useState } from "react";

type Certificate = { certificate_id: string; title: string; issuer: string; completion_date?: string; status: string; verification_url: string };

export default function VerifyCertificate({ params }: { params: Promise<{ publicId: string }> }) {
  const { publicId } = use(params);
  const [data, setData] = useState<Certificate | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { fetch(`/api/v1/certificates/verify/${encodeURIComponent(publicId)}`, { cache: "no-store" }).then(response => response.json()).then(value => { setData(value); setLoading(false); }).catch(() => setLoading(false)); }, [publicId]);
  const found = data && data.status !== "not_found";
  return <main className="mx-auto w-full max-w-3xl px-5 py-16 sm:px-6"><div className="rounded-3xl border border-line bg-surface p-7 text-center shadow-sm sm:p-12"><ShieldCheck className="mx-auto text-primary" size={40} /><p className="mt-5 text-sm font-semibold uppercase tracking-[.18em] text-primary">Public verification</p><h1 className="mt-3 text-3xl font-bold">Certificate status</h1>{loading ? <p className="mt-6 text-muted">Checking the certificate record…</p> : !found ? <div className="mt-8 rounded-2xl border border-amber-500/25 bg-amber-500/10 p-5 text-left text-sm text-amber-700 dark:text-amber-200"><ShieldAlert className="mb-3" size={22} />Certificate not found. The identifier may be invalid or unavailable.</div> : <div className="mt-8 text-left"><div className={`rounded-2xl border p-5 ${data.status === "valid" ? "border-emerald-500/30 bg-emerald-500/10" : "border-red-500/30 bg-red-500/10"}`}><div className="flex items-center gap-3"><CheckCircle2 size={22} className={data.status === "valid" ? "text-emerald-500" : "text-red-500"} /><span className="font-semibold capitalize">{data.status}</span></div><dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2"><div><dt className="text-muted">Certificate</dt><dd className="mt-1 font-semibold">{data.title}</dd></div><div><dt className="text-muted">Issuing organization</dt><dd className="mt-1 font-semibold">{data.issuer}</dd></div><div><dt className="text-muted">Completion date</dt><dd className="mt-1 font-semibold">{data.completion_date ? new Date(data.completion_date).toLocaleDateString() : "—"}</dd></div><div><dt className="text-muted">Certificate ID</dt><dd className="mt-1 break-all font-mono text-xs">{data.certificate_id}</dd></div></dl></div><p className="mt-5 text-xs leading-5 text-muted">This result reflects the current database status. It is not a cryptographic signature or accreditation claim.</p></div>}<Link href="/" className="mt-8 inline-flex text-sm font-semibold text-primary hover:text-primary-hover">Back to Learn-Coding</Link></div></main>;
}
