"use client";

import { ImagePlus, RefreshCw, Trash2, UploadCloud } from "lucide-react";
import { DragEvent, useEffect, useRef, useState } from "react";

const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPTED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function csrf() {
  return document.cookie.match(/(?:^|; )cm_csrf=([^;]+)/)?.[1] ?? "";
}

function errorMessage(value: unknown) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(item => (item && typeof item === "object" && "msg" in item ? item.msg : String(item))).join(", ");
  return "The image upload could not be completed.";
}

type Props = {
  courseId?: string;
  courseTitle: string;
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
};

export function CourseCoverUpload({ courseId, courseTitle, value, disabled = false, onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [localPreview, setLocalPreview] = useState("");
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const preview = localPreview || value;

  useEffect(() => () => { if (localPreview) URL.revokeObjectURL(localPreview); }, [localPreview]);

  function validate(file: File) {
    if (!ACCEPTED_TYPES.has(file.type)) return "Choose a JPG, PNG, or WebP image.";
    if (file.size > MAX_BYTES) return "Course cover images must be 5 MB or smaller.";
    return "";
  }

  function upload(file: File) {
    if (!courseId) {
      setError("Save the course draft before uploading a cover image.");
      return;
    }
    const validationError = validate(file);
    if (validationError) {
      setError(validationError);
      setMessage("");
      return;
    }
    if (localPreview) URL.revokeObjectURL(localPreview);
    setLocalPreview(URL.createObjectURL(file));
    setBusy(true); setProgress(0); setError(""); setMessage("");
    const request = new XMLHttpRequest();
    request.open("POST", `/api/v1/admin/courses/${courseId}/thumbnail`);
    request.withCredentials = true;
    request.setRequestHeader("X-CSRF-Token", csrf());
    request.upload.onprogress = event => { if (event.lengthComputable) setProgress(Math.round((event.loaded / event.total) * 100)); };
    request.onload = () => {
      let body: { thumbnail?: string; detail?: unknown } = {};
      try { body = JSON.parse(request.responseText); } catch { /* handled by status */ }
      if (request.status >= 200 && request.status < 300 && body.thumbnail) {
        onChange(body.thumbnail);
        if (localPreview) URL.revokeObjectURL(localPreview);
        setLocalPreview(""); setProgress(100); setMessage("Course cover uploaded and saved.");
      } else {
        setError(errorMessage(body.detail));
      }
      setBusy(false);
    };
    request.onerror = () => { setBusy(false); setError("The upload service is unavailable. Try again."); };
    const data = new FormData();
    data.append("image", file, file.name);
    request.send(data);
  }

  function drop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault(); setDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) upload(file);
  }

  async function remove() {
    if (!courseId || !value || !window.confirm("Remove this course cover image?")) return;
    setBusy(true); setError(""); setMessage("");
    try {
      const response = await fetch(`/api/v1/admin/courses/${courseId}/thumbnail`, { method: "DELETE", credentials: "include", headers: { "X-CSRF-Token": csrf() } });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(errorMessage(body.detail));
      onChange(""); setMessage("Course cover removed.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The course cover could not be removed.");
    } finally { setBusy(false); }
  }

  return <div className="lg:col-span-2 rounded-2xl border border-line bg-ink/50 p-4 sm:p-5">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><h2 className="text-sm font-semibold">Course Cover Image</h2><p className="mt-1 text-xs text-muted">JPG, PNG, or WebP · maximum 5 MB · 16:9 recommended</p></div>
      {courseId && value && <button type="button" disabled={busy || disabled} onClick={() => void remove()} className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-red-600 transition hover:bg-red-500/10 dark:text-red-200"><Trash2 size={14} /> Remove image</button>}
    </div>
    <div className="mt-4 grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
      <div onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={drop} className={`relative flex aspect-video min-h-40 items-center justify-center overflow-hidden rounded-xl border-2 border-dashed transition ${dragging ? "border-primary bg-primary/10" : "border-line bg-surface"}`}>
        {preview ? <img src={preview} alt={`${courseTitle || "Course"} cover preview`} className="h-full w-full object-cover" /> : <div className="text-center text-muted"><ImagePlus className="mx-auto" size={28} /><p className="mt-2 text-sm">Drag an image here</p><p className="mt-1 text-xs">or choose a file</p></div>}
        {busy && <div className="absolute inset-x-0 bottom-0 bg-slate-950/75 p-3 text-xs text-white"><div className="mb-1 flex justify-between"><span>Uploading…</span><span>{progress}%</span></div><div className="h-1.5 overflow-hidden rounded-full bg-white/20"><div className="h-full rounded-full bg-primary transition-[width]" style={{ width: `${progress}%` }} /></div></div>}
      </div>
      <div className="flex flex-col justify-center gap-3">
        <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" disabled={busy || disabled || !courseId} onChange={event => { const file = event.target.files?.[0]; if (file) upload(file); event.currentTarget.value = ""; }} />
        <button type="button" disabled={busy || disabled || !courseId} onClick={() => inputRef.current?.click()} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"><UploadCloud size={17} /> {value ? "Replace image" : "Choose file"}</button>
        {!courseId && <p className="text-center text-xs leading-5 text-muted">Create the course draft first, then upload its cover.</p>}
        {value && !busy && <p className="flex items-center justify-center gap-2 text-xs text-emerald-700 dark:text-emerald-200"><RefreshCw size={13} /> Saved to this course</p>}
      </div>
    </div>
    {message && <p role="status" className="mt-3 text-sm text-emerald-700 dark:text-emerald-200">{message}</p>}
    {error && <p role="alert" className="mt-3 text-sm text-red-700 dark:text-red-200">{error}</p>}
  </div>;
}
