"use client";

import { useEffect, useRef, useState } from "react";
import { api, lessonQuizApi } from "@/lib/api";
import type { CourseProgress, Lesson, LessonQuiz } from "@/lib/types";
import { csrf } from "@/components/auth-form";
import { LessonContent, CodeSample } from "@/components/lesson-content";
import { LessonTranslationToggle } from "@/components/translation";
import { HtmlPlayground } from "@/components/html-playground";
import { CssPlayground } from "@/components/css-playground";
import { JavascriptPlayground } from "@/components/javascript-playground";
import { PythonPlayground } from "@/components/python-playground";
import { JavaPlayground } from "@/components/java-playground";
import { AdvancedJavaLab } from "@/components/advanced-java-lab";
import { JqueryPlayground } from "@/components/jquery-playground";

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-1.5 overflow-hidden rounded-full bg-elevated" role="progressbar" aria-label="Lesson completion" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(value)}>
      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  );
}

export function LessonReader({ lesson, courseSlug, courseTitle, moduleTitle, modulePosition }: { lesson: Lesson; courseSlug: string; courseTitle: string; moduleTitle?: string; modulePosition?: number }) {
  const [showMyanmar, setShowMyanmar] = useState(false);
  const [exampleIndex, setExampleIndex] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [message, setMessage] = useState("");
  const [quiz, setQuiz] = useState<LessonQuiz | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [quizResult, setQuizResult] = useState<{ score: number; total: number; feedback: { question_id: string; correct: boolean; explanation: string }[] } | null>(null);
  const [quizLoading, setQuizLoading] = useState(true);
  const [quizSubmitting, setQuizSubmitting] = useState(false);
  const [progress, setProgress] = useState<CourseProgress | null>(null);
  const example = lesson.code_examples[exampleIndex];
  const visitedLesson = useRef<string | null>(null);

  const lessonProgress = progress?.lessons.find(item => item.lesson_id === lesson.id);
  const percentage = progress && progress.total_lessons ? (progress.completed_lessons / progress.total_lessons) * 100 : 0;

  useEffect(() => {
    let active = true;
    lessonQuizApi.get(lesson.id).then(value => { if (active) setQuiz(value); }).catch(() => { if (active) setQuiz(null); }).finally(() => { if (active) setQuizLoading(false); });
    return () => { active = false; };
  }, [lesson.id]);

  useEffect(() => {
    let active = true;
    api.courseProgress(courseSlug)
      .then(value => {
        if (!active) return;
        setProgress(value);
        setCompleted(value.lessons.find(item => item.lesson_id === lesson.id)?.completed ?? false);
      })
      .catch(() => { if (active) setProgress(null); });
    if (visitedLesson.current !== lesson.id) {
      visitedLesson.current = lesson.id;
      api.visitLesson(lesson.id, csrf()).catch(() => { /* Anonymous visitors and non-enrolled students simply do not record a visit. */ });
    }
    return () => { active = false; };
  }, [courseSlug, lesson.id]);

  async function complete() {
    setMessage("");
    try {
      await api.progress(lesson.id, true, csrf());
      setCompleted(true);
      setMessage("Lesson marked complete.");
      api.courseProgress(courseSlug).then(setProgress).catch(() => {});
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Sign in and enroll to save progress.");
    }
  }
  async function toggleBookmark() {
    setMessage("");
    try {
      const result = await api.bookmark(lesson.id, csrf());
      setBookmarked(result.bookmarked);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Sign in to bookmark this lesson.");
    }
  }

  const allAnswered = Boolean(quiz && Object.keys(answers).length === quiz.questions.length);

  return (
    <div>
      <div className="sticky top-[73px] z-30 -mx-2 mb-6 border-b border-line bg-ink/95 px-2 py-3 backdrop-blur-xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs text-slate-500">
              <span className="text-indigo-300">{courseTitle}</span> · Lesson {lesson.order_index}
              {moduleTitle ? ` · Module ${modulePosition ?? ""} ${moduleTitle}` : ""}
            </p>
            <div className="mt-2 flex items-center gap-3">
              <div className="w-full max-w-xs"><ProgressBar value={percentage} /></div>
              <span className="shrink-0 text-[11px] text-slate-500">
                {progress ? `${progress.completed_lessons}/${progress.total_lessons} complete` : "Sign in and enroll to save progress"}
              </span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <LessonTranslationToggle onChange={setShowMyanmar} />
            <button
              onClick={toggleBookmark}
              className={`rounded-lg border px-3 py-2 text-sm ${bookmarked ? "border-indigo-400 bg-indigo-500/15 text-indigo-200" : "border-line text-slate-300"}`}
              aria-pressed={bookmarked}
            >
              {bookmarked ? "Bookmarked" : "Bookmark"}
            </button>
            <button onClick={complete} disabled={completed} className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold disabled:cursor-default disabled:opacity-60">
              {completed ? "Completed" : "Mark complete"}
            </button>
          </div>
        </div>
        {lessonProgress?.last_visited_at && <p className="mt-2 text-[11px] text-slate-600">Last visited {new Date(lessonProgress.last_visited_at).toLocaleDateString()}</p>}
      </div>

      {message && <p className="mb-5 rounded-lg border border-line bg-surface px-4 py-3 text-sm text-slate-300" role="status">{message}</p>}

      <article aria-label="Lesson content">
        <LessonContent content={lesson.content_en} />
      </article>

      {showMyanmar && (
        <section className="mt-8 rounded-2xl border border-indigo-400/20 bg-indigo-500/5 p-5 sm:p-6" aria-label="Myanmar explanation">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-bold text-indigo-200">မြန်မာရှင်းလင်းချက်</h2>
            <span className="rounded-full bg-indigo-500/15 px-2 py-0.5 text-[11px] text-indigo-300">MM</span>
          </div>
          {lesson.content_mm
            ? <LessonContent content={lesson.content_mm} />
            : <p className="leading-8 text-slate-300">Myanmar explanation is not available for this lesson yet.</p>}
        </section>
      )}

      {lesson.code_examples.length > 0 && (
        <section className="mt-10" aria-label="Explained code examples">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold">Explained examples</h2>
              <p className="mt-1 text-sm text-slate-500">Read the code and expected behavior before trying it yourself.</p>
            </div>
            <div className="flex flex-wrap gap-2" role="tablist" aria-label="Code examples">
              {lesson.code_examples.map((item, index) => (
                <button
                  key={item.id}
                  role="tab"
                  aria-selected={index === exampleIndex}
                  onClick={() => setExampleIndex(index)}
                  className={`rounded-lg px-3 py-2 text-xs ${index === exampleIndex ? "bg-indigo-500/20 text-indigo-200" : "bg-surface text-slate-400"}`}
                >
                  Example {index + 1}
                </button>
              ))}
            </div>
          </div>
          {example && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-slate-200">{example.title}</h3>
              <CodeSample code={example.code} language={example.language} label={example.filename ?? example.language.toUpperCase()} />
              {example.description && <div className="mt-3 whitespace-pre-line rounded-xl border border-line bg-surface/60 p-5 text-sm leading-7 text-slate-300">{example.description}</div>}
            </div>
          )}
        </section>
      )}

      {courseSlug === "html" && lesson.code_examples.some(item => item.language.toLowerCase() === "html") && (
        <HtmlPlayground
          title={`${lesson.title} practice`}
          examples={lesson.code_examples
            .filter(item => item.language.toLowerCase() === "html")
            .map(item => ({ title: item.title, code: item.code }))}
        />
      )}

      {courseSlug === "css" && lesson.code_examples.some(item => item.language.toLowerCase() === "css") && (
        <CssPlayground
          title={`${lesson.title} practice`}
          examples={[{
            title: lesson.title,
            html: lesson.code_examples.find(item => item.language.toLowerCase() === "html")?.code ?? "<main><h1>CSS practice</h1><p>Edit the CSS.</p></main>",
            css: lesson.code_examples.find(item => item.language.toLowerCase() === "css")?.code ?? "",
          }]}
        />
      )}

      {courseSlug === "javascript" && lesson.code_examples.some(item => item.language.toLowerCase() === "javascript") && (
        <JavascriptPlayground
          title={`${lesson.title} practice`}
          code={lesson.code_examples.find(item => item.language.toLowerCase() === "javascript")?.code ?? ""}
        />
      )}

      {courseSlug === "python" && lesson.code_examples.some(item => item.language.toLowerCase() === "python") && (
        <PythonPlayground
          title={`${lesson.title} practice`}
          code={lesson.code_examples.find(item => item.language.toLowerCase() === "python")?.code ?? ""}
        />
      )}

      {courseSlug === "java" && lesson.code_examples.some(item => item.language.toLowerCase() === "java") && (
        <JavaPlayground
          title={`${lesson.title} practice`}
          code={lesson.code_examples.find(item => item.language.toLowerCase() === "java")?.code ?? ""}
        />
      )}

      {courseSlug === "advanced-java" && lesson.code_examples.some(item => item.language.toLowerCase() === "java") && (
        <AdvancedJavaLab
          files={lesson.code_examples.filter(item => item.language.toLowerCase() === "java").map(item => ({ filename: item.filename ?? "Main.java", code: item.code, language: item.language }))}
        />
      )}

      {courseSlug === "jquery" && lesson.code_examples.some(item => item.language.toLowerCase() === "jquery") && (
        <JqueryPlayground
          title={`${lesson.title} practice`}
          code={lesson.code_examples.find(item => item.language.toLowerCase() === "jquery")?.code ?? ""}
        />
      )}

      {!quizLoading && quiz && (
        <section className="mt-10 rounded-2xl bg-surface p-5 sm:p-6" aria-labelledby="lesson-quiz-title">
          <h2 id="lesson-quiz-title" className="text-xl font-bold">{quiz.title}</h2>
          <p className="mt-2 text-sm text-slate-400">Answer the questions, then submit to save a real attempt. Your score is stored with your account.</p>
          {quiz.latest_attempt && <p className="mt-2 text-xs text-slate-500">Previous attempt: {quiz.latest_attempt.score}/{quiz.latest_attempt.total}</p>}
          <div className="mt-5 space-y-6">
            {quiz.questions.map(question => (
              <fieldset key={question.id}>
                <legend className="font-medium text-slate-200">{question.position}. {question.prompt}</legend>
                <div className="mt-3 space-y-2">
                  {question.options.map(option => (
                    <label className="flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5" key={option}>
                      <input
                        type="radio"
                        name={question.id}
                        value={option}
                        checked={answers[question.id] === option}
                        onChange={() => setAnswers(current => ({ ...current, [question.id]: option }))}
                      />
                      {option}
                    </label>
                  ))}
                </div>
              </fieldset>
            ))}
          </div>
          <button
            className="mt-6 rounded-lg bg-primary px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!allAnswered || quizSubmitting}
            onClick={async () => {
              setQuizSubmitting(true);
              setMessage("");
              try {
                const result = await lessonQuizApi.submit(lesson.id, answers, csrf());
                setQuizResult(result);
              } catch (error) {
                setMessage(error instanceof Error ? error.message : "Sign in and enroll to submit this quiz.");
              } finally {
                setQuizSubmitting(false);
              }
            }}
          >
            {quizSubmitting ? "Submitting…" : "Submit quiz"}
          </button>
          {quizResult && (
            <div className="mt-5 rounded-xl border border-line p-4" role="status" aria-live="polite">
              <p className="font-semibold">Score: {quizResult.score}/{quizResult.total}</p>
              <div className="mt-3 space-y-2 text-sm text-slate-400">
                {quizResult.feedback.map(item => (
                  <p key={item.question_id} className={item.correct ? "text-emerald-300" : "text-amber-200"}>
                    {item.correct ? "Correct" : "Review"}: {item.explanation}
                  </p>
                ))}
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
