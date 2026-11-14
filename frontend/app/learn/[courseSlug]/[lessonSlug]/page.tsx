import Link from "next/link";
import { notFound } from "next/navigation";
import { api, courseLearningApi } from "@/lib/api";
import type { CourseLearning, Lesson } from "@/lib/types";
import { LessonReader } from "@/components/lesson-reader";
import { LearningSidebar } from "@/components/learning-sidebar";

export default async function LessonPage({ params }: { params: Promise<{ courseSlug: string; lessonSlug: string }> }) {
  const { courseSlug, lessonSlug } = await params;
  let course: CourseLearning;
  let lesson: Lesson;
  try {
    try {
      [course, lesson] = await Promise.all([
        courseLearningApi.course(courseSlug),
        courseLearningApi.lesson(courseSlug, lessonSlug),
      ]);
    } catch {
      // Compatibility with an already-running API process that has not been
      // restarted with the lightweight endpoints yet. The fallback is slower,
      // but keeps published lessons reachable until the service is restarted.
      const fullCourse = await api.course(courseSlug);
      const fullLesson = fullCourse.modules.flatMap(module => module.lessons).find(item => item.slug === lessonSlug);
      if (!fullLesson) notFound();
      course = {
        ...fullCourse,
        modules: fullCourse.modules.map(module => ({
          ...module,
          lessons: module.lessons.map(item => ({ id: item.id, title: item.title, slug: item.slug, order_index: item.order_index, duration_minutes: item.duration_minutes ?? 30 })),
        })),
      };
      lesson = fullLesson;
    }
  } catch {
    notFound();
  }
  const lessons = course.modules.flatMap(module => module.lessons);
  const index = lessons.findIndex(item => item.id === lesson.id);
  const currentModule = course.modules.find(module => module.lessons.some(item => item.id === lesson.id));

  return (
    <section className="mx-auto grid max-w-7xl gap-8 px-5 py-8 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-8">
      <LearningSidebar courseSlug={courseSlug} courseTitle={course.title} modules={course.modules} currentLessonId={lesson.id} />
      <article className="min-w-0">
        <Link className="text-sm text-indigo-300 hover:text-white" href={`/courses/${courseSlug}`}>← Course overview</Link>
        <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-sm text-slate-500">
              {currentModule ? `Module ${currentModule.order_index} · ` : ""}Lesson {lesson.order_index} · {course.language.name} · {lesson.duration_minutes ?? 30} min
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">{lesson.title}</h1>
          </div>
          <span className="rounded-full border border-line px-3 py-1 text-xs text-slate-400">Read · practice · compile</span>
        </div>

        <div className="mt-8">
          <LessonReader
            key={lesson.id}
            lesson={lesson}
            courseSlug={courseSlug}
            courseTitle={course.title}
            moduleTitle={currentModule?.title}
            modulePosition={currentModule?.order_index}
          />
        </div>

        <nav className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-6 text-sm" aria-label="Lesson navigation">
          {lessons[index - 1] ? (
            <Link className="rounded-lg border border-line px-4 py-2 text-slate-300 hover:border-indigo-400 hover:text-white" href={`/learn/${courseSlug}/${lessons[index - 1].slug}`}>
              ← Previous: {lessons[index - 1].title}
            </Link>
          ) : <span />}
          {lessons[index + 1] ? (
            <Link className="rounded-lg bg-primary px-4 py-2 font-semibold text-white hover:bg-indigo-500" href={`/learn/${courseSlug}/${lessons[index + 1].slug}`}>
              Next: {lessons[index + 1].title} →
            </Link>
          ) : (
            <Link className="rounded-lg bg-primary px-4 py-2 font-semibold text-white hover:bg-indigo-500" href={`/courses/${courseSlug}`}>
              Back to course overview →
            </Link>
          )}
        </nav>
      </article>
    </section>
  );
}
