"use client";

import { useState } from "react";
import { csrf } from "@/components/auth-form";
import { projectApi } from "@/lib/project-api";
import { Card } from "@/components/ui";

type Submission = {
  id: string;
  status: string;
  repository_url: string;
  branch_or_sha: string;
  demo_url?: string | null;
  project_description?: string;
  setup_instructions?: string;
  submitted_at: string;
  review?: { decision: string; comments: string; total_score?: number | null } | null;
};

type Props = {
  projectId: string;
  projectStatus: string;
  progress: { completed: number; total: number };
  submissions: Submission[];
  onRefresh: () => Promise<void>;
};

const statusLabels: Record<string, string> = {
  submitted: "Submitted",
  in_review: "Under review",
  changes_requested: "Needs changes",
  approved: "Approved",
  rejected: "Rejected",
};

const statusTone: Record<string, string> = {
  submitted: "border-indigo-400/30 bg-indigo-500/10 text-indigo-200",
  in_review: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  changes_requested: "border-orange-400/30 bg-orange-500/10 text-orange-200",
  approved: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
  rejected: "border-red-400/30 bg-red-500/10 text-red-200",
};

function label(status: string) { return statusLabels[status] ?? status.replaceAll("_", " "); }

export function ProjectSubmissionPanel({ projectId, projectStatus, progress, submissions, onRefresh }: Props) {
  const [method, setMethod] = useState("repository");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const latest = submissions[0];
  const canResubmit = latest?.status === "changes_requested" || latest?.status === "rejected";
  const blocked = latest && ["submitted", "in_review", "approved"].includes(latest.status);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(""); setMessage("");
    if (method !== "repository") { setError("This submission method is not available for this project yet."); return; }
    setSubmitting(true);
    try {
      const body = Object.fromEntries(new FormData(event.currentTarget));
      await projectApi.submit(projectId, body, csrf());
      event.currentTarget.reset();
      await onRefresh();
      setMessage(canResubmit ? "Resubmission sent for review." : "Submission sent for review.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to submit project"); }
    finally { setSubmitting(false); }
  };

  return <div className="space-y-5">
    <div id="submission"><Card className="p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-300">Submission</p><h2 className="mt-2 text-xl font-bold">Send your project for review</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Your current workspace progress is preserved. A submission is a review request and does not change your source files.</p></div>
        {latest && <span className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${statusTone[latest.status] ?? "border-line text-slate-300"}`}>{label(latest.status)}</span>}
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3" role="radiogroup" aria-label="Submission method">
        <button type="button" role="radio" aria-checked={method === "repository"} onClick={() => setMethod("repository")} className={`rounded-xl border p-4 text-left transition ${method === "repository" ? "border-indigo-400/70 bg-indigo-500/10" : "border-line bg-ink hover:border-indigo-400/40"}`}><span className="font-semibold">Repository URL</span><span className="mt-1 block text-xs text-slate-400">Available · HTTPS GitHub link</span></button>
        <button type="button" role="radio" aria-checked={false} disabled className="cursor-not-allowed rounded-xl border border-line bg-ink p-4 text-left opacity-55"><span className="font-semibold">Saved workspace</span><span className="mt-1 block text-xs text-slate-500">Unavailable until snapshots are enabled</span></button>
        <button type="button" role="radio" aria-checked={false} disabled className="cursor-not-allowed rounded-xl border border-line bg-ink p-4 text-left opacity-55"><span className="font-semibold">File / ZIP upload</span><span className="mt-1 block text-xs text-slate-500">Unavailable until private storage is enabled</span></button>
      </div>
      {blocked ? <div className="mt-5 rounded-xl border border-line bg-ink p-4 text-sm leading-6 text-slate-400">{latest.status === "approved" ? "This project has already been approved. Previous submissions remain available below." : "A submission is already awaiting review. You can submit again after the reviewer requests changes."}</div> : <form className="mt-5 space-y-3" onSubmit={submit}>
        <label className="block text-sm font-medium text-slate-200">Repository URL<input required name="repository_url" type="url" pattern="https://(www\\.)?github\\.com/.+" placeholder="https://github.com/you/repository" className="mt-2 w-full rounded-xl border border-line bg-ink px-4 py-3 text-sm outline-none focus:border-indigo-400" /></label>
        <div className="grid gap-3 sm:grid-cols-2"><label className="block text-sm font-medium text-slate-200">Branch or commit SHA<input required name="branch_or_sha" minLength={1} maxLength={180} placeholder="main" className="mt-2 w-full rounded-xl border border-line bg-ink px-4 py-3 text-sm outline-none focus:border-indigo-400" /></label><label className="block text-sm font-medium text-slate-200">Demo URL <span className="text-slate-500">(optional)</span><input name="demo_url" type="url" placeholder="https://example.com" className="mt-2 w-full rounded-xl border border-line bg-ink px-4 py-3 text-sm outline-none focus:border-indigo-400" /></label></div>
        <label className="block text-sm font-medium text-slate-200">Project summary<textarea name="project_description" placeholder="What did you build?" rows={4} className="mt-2 w-full rounded-xl border border-line bg-ink px-4 py-3 text-sm outline-none focus:border-indigo-400" /></label>
        <label className="block text-sm font-medium text-slate-200">Setup instructions<textarea name="setup_instructions" placeholder="How should an instructor run it?" rows={3} className="mt-2 w-full rounded-xl border border-line bg-ink px-4 py-3 text-sm outline-none focus:border-indigo-400" /></label>
        <p className="text-xs text-slate-500">Progress: {progress.completed} of {progress.total} required tasks. The server validates access and submission state.</p>
        {error && <p className="text-sm text-red-300" role="alert">{error}</p>}{message && <p className="text-sm text-emerald-300" role="status">{message}</p>}
        <button disabled={submitting} className="rounded-xl bg-indigo-500 px-4 py-3 text-sm font-semibold transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60">{submitting ? "Sending…" : canResubmit ? "Submit new attempt" : "Submit project"}</button>
      </form>}
    </Card></div>
    <Card className="p-6"><div className="flex items-center justify-between gap-3"><div><h2 className="text-xl font-bold">Submission history</h2><p className="mt-1 text-sm text-slate-400">Every review request remains visible to you.</p></div><span className="text-sm text-slate-500">{submissions.length} attempt{submissions.length === 1 ? "" : "s"}</span></div>
      <div className="mt-5 space-y-3">{submissions.map((submission, index) => <article key={submission.id} className="rounded-xl border border-line bg-ink p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><span className="text-sm font-semibold text-slate-200">Attempt {submissions.length - index}</span><span className={`rounded-full border px-2.5 py-1 text-xs ${statusTone[submission.status] ?? "border-line text-slate-300"}`}>{label(submission.status)}</span></div><time className="text-xs text-slate-500" dateTime={submission.submitted_at}>{new Date(submission.submitted_at).toLocaleString()}</time></div><p className="mt-3 break-all text-sm text-slate-400">{submission.repository_url} · {submission.branch_or_sha}</p>{submission.review && <div className="mt-3 rounded-lg border border-line/70 p-3 text-sm"><p className="text-indigo-200">{submission.review.comments || "Reviewer decision recorded."}</p>{submission.review.total_score != null && <p className="mt-1 font-semibold text-emerald-300">Final score: {submission.review.total_score}/100</p>}</div>}</article>)}{!submissions.length && <p className="rounded-xl bg-ink p-4 text-sm text-slate-400">No submissions yet. Submit a repository when your project is ready.</p>}</div>
    </Card>
    <Card className="p-6"><h2 className="text-lg font-bold">Submission lifecycle</h2><div className="mt-4 grid gap-3 sm:grid-cols-5">{["submitted", "in_review", "changes_requested", "approved"].map((status, index) => <div key={status} className="flex items-center gap-3 text-xs text-slate-400"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/15 font-bold text-indigo-200">{index + 1}</span><span>{label(status)}</span></div>)}</div><p className="mt-4 text-xs leading-5 text-slate-500">Automated grading and private file uploads are not enabled by the current backend. No score is shown unless an authorized instructor records one.</p></Card>
  </div>;
}
