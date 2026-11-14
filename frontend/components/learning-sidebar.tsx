"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { CourseProgress, LearningModule } from "@/lib/types";

function ProgressBar({ value, label }: { value: number; label: string }) {
  return (
    <div>
      <div className="flex items-center justify-between text-[11px] text-slate-500">
        <span>{label}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-elevated" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(value)}>
        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
      </div>
    </div>
  );
}

export function LearningSidebar({ courseSlug, courseTitle, modules, currentLessonId }: { courseSlug: string; courseTitle: string; modules: LearningModule[]; currentLessonId: string }) {
  const [progress, setProgress] = useState<CourseProgress | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [openModules, setOpenModules] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let active = true;
    api.courseProgress(courseSlug).then(value => { if (active) setProgress(value); }).catch(() => { if (active) setProgress(null); });
    return () => { active = false; };
  }, [courseSlug]);

  useEffect(() => {
    setOpenModules(current => {
      const next = { ...current };
      modules.forEach(module => {
        if (!(module.id in next)) next[module.id] = module.order_index === 1 || module.lessons.some(lesson => lesson.id === currentLessonId);
      });
      return next;
    });
  }, [modules, currentLessonId]);

  const completedIds = useMemo(() => new Set(progress?.lessons.filter(item => item.completed).map(item => item.lesson_id) ?? []), [progress]);
  const moduleProgress = useMemo(() => new Map(progress?.modules.map(item => [item.module_id, item]) ?? []), [progress]);
  const currentModule = modules.find(module => module.lessons.some(lesson => lesson.id === currentLessonId));
  const currentLessonNumber = modules.flatMap(module => module.lessons).findIndex(lesson => lesson.id === currentLessonId) + 1;
  const totalLessons = modules.reduce((total, module) => total + module.lessons.length, 0);

  return (
    <aside className="lg:sticky lg:top-[89px] lg:self-start" aria-label="Course contents">
      <div className="rounded-2xl border border-line bg-surface p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate text-xs font-semibold uppercase tracking-widest text-slate-500">{courseTitle}</p>
            <p className="mt-1 text-xs text-slate-500">{totalLessons} lessons{progress ? ` · ${progress.completed_lessons} complete` : ""}</p>
          </div>
          <button
            type="button"
            onClick={() => setSidebarOpen(current => !current)}
            className="rounded-lg border border-line px-2 py-1 text-xs text-slate-300 transition hover:border-indigo-400 hover:text-white"
            aria-expanded={sidebarOpen}
            aria-controls="course-contents-list"
          >
            {sidebarOpen ? "Collapse" : "Contents"}
          </button>
        </div>
        {progress && <div className="mt-3"><ProgressBar value={progress.progress_percent} label="Course progress" /></div>}
        {sidebarOpen && (
          <div id="course-contents-list" className="mt-4 max-h-[calc(100vh-220px)] space-y-2 overflow-y-auto pr-1">
            {modules.map(module => {
              const isOpen = openModules[module.id] ?? false;
              const stats = moduleProgress.get(module.id);
              const completed = stats?.completed_lessons ?? module.lessons.filter(lesson => completedIds.has(lesson.id)).length;
              return (
                <div key={module.id} className="rounded-xl bg-elevated/60">
                  <button
                    type="button"
                    onClick={() => setOpenModules(current => ({ ...current, [module.id]: !isOpen }))}
                    className="flex w-full items-center justify-between gap-2 px-3 py-2.5 text-left text-sm"
                    aria-expanded={isOpen}
                  >
                    <span className={`min-w-0 truncate font-medium ${currentModule?.id === module.id ? "text-indigo-200" : "text-slate-300"}`}>
                      {module.order_index}. {module.title}
                    </span>
                    <span className="shrink-0 text-[11px] text-slate-500">{completed}/{module.lessons.length} {isOpen ? "−" : "+"}</span>
                  </button>
                  {isOpen && (
                    <div className="space-y-0.5 px-2 pb-2">
                      {module.lessons.map(lesson => {
                        const active = lesson.id === currentLessonId;
                        const done = completedIds.has(lesson.id);
                        return (
                          <Link
                            className={`flex items-start gap-2 rounded-lg px-2.5 py-2 text-xs leading-5 transition ${active ? "bg-indigo-500/15 text-indigo-200" : "text-slate-400 hover:bg-white/5 hover:text-slate-200"}`}
                            href={`/learn/${courseSlug}/${lesson.slug}`}
                            aria-current={active ? "page" : undefined}
                            key={lesson.id}
                          >
                            <span aria-hidden="true" className={done ? "text-emerald-300" : "text-slate-600"}>{done ? "✓" : "○"}</span>
                            <span className="min-w-0">{lesson.order_index}. {lesson.title}</span>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
        {progress && currentModule && (
          <p className="mt-3 border-t border-line pt-3 text-[11px] text-slate-500">
            Lesson {currentLessonNumber} of {totalLessons} · Module {currentModule.order_index}
          </p>
        )}
      </div>
    </aside>
  );
}
