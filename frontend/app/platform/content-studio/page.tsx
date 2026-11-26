"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  CircleAlert,
  Check,
  Clock,
  FileText,
  RefreshCw,
  Settings,
  Sparkles,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { contentStudioApi } from "@/lib/api";
import { Badge, Button, Card, Skeleton } from "@/components/ui";

type PlatformContentDashboard = {
  metrics: {
    projects: number;
    jobs: number;
    pending_reviews: number;
    quality_issues: number;
  };
  ai_status: string;
  data_source: string;
};

const metricMeta = [
  {
    key: "projects",
    label: "Content projects",
    detail: "Tracked in the studio",
    icon: BookOpen,
    tone: "text-indigo-300",
    href: "/platform/content-studio",
  },
  {
    key: "jobs",
    label: "Generation jobs",
    detail: "Queued or completed",
    icon: Clock,
    tone: "text-cyan-300",
    href: "/instructor/content-studio/usage",
  },
  {
    key: "pending_reviews",
    label: "Pending reviews",
    detail: "Waiting for approval",
    icon: FileText,
    tone: "text-amber-300",
    href: "/platform/content-review",
  },
  {
    key: "quality_issues",
    label: "Quality issues",
    detail: "Failed quality checks",
    icon: CircleAlert,
    tone: "text-rose-300",
    href: "/instructor/content-studio/quality",
  },
] as const;

export default function Page() {
  const [data, setData] = useState<PlatformContentDashboard | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    contentStudioApi
      .platform()
      .then((value) => setData(value as PlatformContentDashboard))
      .catch((value) =>
        setError(
          value instanceof Error
            ? value.message
            : "Unable to load content studio health.",
        ),
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading && !data) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-36" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <Skeleton className="h-32" key={item} />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </section>
    );
  }

  if (error && !data) {
    return (
      <section className="space-y-5">
        <Card className="border-rose-400/20 bg-rose-500/[.04] p-6">
          <div className="flex items-start gap-4">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-rose-500/10 text-rose-300">
              <CircleAlert size={19} />
            </div>
            <div>
              <p className="text-sm font-semibold text-rose-200">
                Content studio is unavailable
              </p>
              <p className="mt-1 text-sm leading-6 text-slate-400">{error}</p>
              <Button onClick={load} className="mt-4 inline-flex items-center gap-2">
                <RefreshCw size={15} />
                Try again
              </Button>
            </div>
          </div>
        </Card>
      </section>
    );
  }

  if (!data) return null;

  const providerConfigured = data.ai_status.toLowerCase() === "configured";

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-indigo-300">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-indigo-500/10">
              <Sparkles size={15} />
            </span>
            Platform content control
          </div>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-[38px]">
            Generation and review health
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            See the current content pipeline, review queue, and quality signals from
            the platform database.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={load}
            className="inline-flex items-center gap-2 border border-line bg-surface text-slate-200 hover:bg-elevated"
          >
            <RefreshCw size={15} />
            Refresh
          </Button>
          <Link
            href="/platform/content-review"
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
          >
            Open review queue
            <ArrowRight size={15} />
          </Link>
        </div>
      </div>

      {error && (
        <Card className="border-amber-400/20 bg-amber-400/[.04] p-4 text-sm text-amber-200">
          The latest refresh failed: {error}
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metricMeta.map(({ key, label, detail, icon: Icon, tone, href }) => (
          <Link href={href} key={key}>
            <Card className="group relative h-full overflow-hidden p-5 transition hover:-translate-y-0.5 hover:border-indigo-400/30">
              <div className="absolute right-4 top-4 rounded-xl bg-white/[.03] p-2">
                <Icon size={17} className={tone} />
              </div>
              <p className="text-xs font-medium text-slate-500">{label}</p>
              <p className="mt-3 text-3xl font-bold tracking-tight text-slate-50">
                {data.metrics[key].toLocaleString()}
              </p>
              <p className="mt-1 text-xs text-slate-500">{detail}</p>
              <span className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-indigo-300 opacity-0 transition group-hover:opacity-100">
                View details
                <ArrowRight size={13} />
              </span>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,.8fr)]">
        <Card className="p-6 sm:p-7">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[.18em] text-slate-500">
                Workflow
              </p>
              <h2 className="mt-2 text-xl font-semibold">From draft to publication</h2>
              <p className="mt-1 text-sm text-slate-400">
                Every generated item remains reviewable before it reaches learners.
              </p>
            </div>
            <Check className="text-emerald-300" size={20} />
          </div>
          <div className="mt-7 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-line bg-ink/40 p-4">
              <span className="text-xs font-semibold text-indigo-300">01</span>
              <h3 className="mt-3 text-sm font-semibold">Create draft</h3>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Write or generate editable content.
              </p>
            </div>
            <div className="rounded-xl border border-line bg-ink/40 p-4">
              <span className="text-xs font-semibold text-amber-300">02</span>
              <h3 className="mt-3 text-sm font-semibold">Independent review</h3>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Check structure, examples, and quality.
              </p>
            </div>
            <div className="rounded-xl border border-line bg-ink/40 p-4">
              <span className="text-xs font-semibold text-emerald-300">03</span>
              <h3 className="mt-3 text-sm font-semibold">Publish</h3>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Release only approved revisions.
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6 sm:p-7">
          <div className="flex items-start gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-amber-400/10 text-amber-300">
              <Settings size={18} />
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[.18em] text-slate-500">
                Provider status
              </p>
              <h2 className="mt-2 text-xl font-semibold">AI generation</h2>
            </div>
          </div>
          <Badge
            className={`mt-5 inline-flex ${
              providerConfigured
                ? "bg-emerald-400/10 text-emerald-300"
                : "bg-amber-400/10 text-amber-200"
            }`}
          >
            {data.ai_status}
          </Badge>
          <p className="mt-4 text-sm leading-6 text-slate-400">
            Manual content editing and review remain available while an AI provider is
            not configured.
          </p>
          <Link
            href="/platform/settings"
            className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-indigo-300 hover:text-indigo-200"
          >
            View platform settings
            <ArrowRight size={15} />
          </Link>
          <p className="mt-6 border-t border-line/70 pt-4 text-xs text-slate-600">
            Data source: {data.data_source}
          </p>
        </Card>
      </div>
    </section>
  );
}
