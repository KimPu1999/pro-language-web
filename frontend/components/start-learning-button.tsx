"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { csrf } from "@/components/auth-form";

export function StartLearningButton({ courseSlug, lessonSlug }: { courseSlug: string; lessonSlug: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const destination = `/learn/${encodeURIComponent(courseSlug)}/${encodeURIComponent(lessonSlug)}`;

  async function start() {
    setBusy(true);
    setError("");
    try {
      // Enrollment is intentionally server-side. A 409 means the student is
      // already enrolled, so it is a successful start action.
      await api.enroll(courseSlug, csrf());
      router.push(destination);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) {
        router.push(destination);
        return;
      }
      if (reason instanceof ApiError && reason.status === 401) {
        router.push(`/login?next=${encodeURIComponent(destination)}`);
        return;
      }
      setError(reason instanceof Error ? reason.message : "Unable to start this course.");
      setBusy(false);
    }
  }

  return (
    <div>
      <button
        type="button"
        className="w-full rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={busy}
        onClick={start}
      >
        {busy ? "Starting…" : "Start learning"}
      </button>
      {error && <p className="mt-3 text-xs text-red-300" role="alert">{error}</p>}
    </div>
  );
}
