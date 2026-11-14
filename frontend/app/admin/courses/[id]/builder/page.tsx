"use client";

import { useEffect, useMemo, useState } from "react";
import { api, adminQuizApi } from "@/lib/api";
import { csrf } from "@/components/auth-form";
import { Badge, Button, Card } from "@/components/ui";
import { LessonContent } from "@/components/lesson-content";
import type { AdminCodeExample, AdminCourse, AdminCurriculumLesson, AdminCurriculumModule, AdminQuiz } from "@/lib/types";

const inputClass = "mt-1 w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm text-slate-200 outline-none transition focus:border-indigo-400";
const textAreaClass = `${inputClass} min-h-28 font-mono leading-6`;

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="font-medium text-slate-300">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  );
}

function splitLines(value: string) {
  return value.split("\n").map(line => line.trim()).filter(Boolean);
}

type CourseForm = Pick<AdminCourse, "title" | "slug" | "short_description" | "description" | "level" | "estimated_duration" | "thumbnail" | "outcomes" | "requirements">;

export default function Builder({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState("");
  const [course, setCourse] = useState<AdminCourse | null>(null);
  const [curriculum, setCurriculum] = useState<AdminCurriculumModule[]>([]);
  const [tab, setTab] = useState("Overview");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState<CourseForm | null>(null);
  const [draft, setDraft] = useState<AdminCurriculumLesson | null>(null);
  const [examples, setExamples] = useState<AdminCodeExample[]>([]);
  const [quiz, setQuiz] = useState<AdminQuiz | null>(null);
  const [preview, setPreview] = useState(false);
  const [previewMyanmar, setPreviewMyanmar] = useState(false);
  const [editorLoading, setEditorLoading] = useState(false);

  useEffect(() => {
    params.then(async p => {
      setId(p.id);
      try {
        const [loadedCourse, loadedCurriculum] = await Promise.all([api.adminBuilder(p.id), api.adminCurriculum(p.id)]);
        setCourse(loadedCourse);
        setForm({
          title: loadedCourse.title,
          slug: loadedCourse.slug,
          short_description: loadedCourse.short_description,
          description: loadedCourse.description,
          level: loadedCourse.level,
          estimated_duration: loadedCourse.estimated_duration,
          thumbnail: loadedCourse.thumbnail ?? null,
          outcomes: loadedCourse.outcomes ?? [],
          requirements: loadedCourse.requirements ?? [],
        });
        setCurriculum(loadedCurriculum);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load the course builder.");
      }
    });
  }, [params]);

  const modules = useMemo(() => [...curriculum].sort((a, b) => a.position - b.position), [curriculum]);
  const selectedModule = draft ? curriculum.find(module => module.lessons.some(lesson => lesson.id === draft.id)) : null;

  function notify(value: string) {
    setMessage(value);
  }

  async function saveCourse() {
    if (!form || !course) return;
    if (form.title.trim().length < 3) { notify("Course title must contain at least 3 characters."); return; }
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(form.slug)) { notify("Slug must use lowercase letters, numbers, and single hyphens."); return; }
    setBusy(true);
    try {
      const updated = await api.adminUpdateCourse(course.id, {
        ...form,
        title: form.title.trim(),
        short_description: form.short_description.trim(),
        description: form.description.trim(),
        outcomes: form.outcomes,
        requirements: form.requirements,
        language_id: course.language_id,
        category_id: course.category_id,
        status: course.status,
      }, csrf());
      setCourse(updated);
      notify("Course details saved.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to save the course.");
    } finally {
      setBusy(false);
    }
  }

  async function decide(decision: "publish" | "in_review" | "draft") {
    if (!course) return;
    setBusy(true);
    try {
      const updated = await api.adminPublish(course.id, { decision, note: "Updated from the course builder" }, csrf());
      setCourse(updated);
      notify(decision === "publish" ? "Course published." : decision === "in_review" ? "Course submitted for review." : "Course returned to draft.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to change publishing state.");
    } finally {
      setBusy(false);
    }
  }

  async function refreshCurriculum(courseId = id) {
    const loaded = await api.adminCurriculum(courseId);
    setCurriculum(loaded);
    return loaded;
  }

  async function addModule() {
    if (!course) return;
    setBusy(true);
    try {
      const position = modules.reduce((highest, module) => Math.max(highest, module.position), 0) + 1;
      await api.adminCreateModule(course.id, { title: `Module ${position}`, position }, csrf());
      await refreshCurriculum();
      notify("Module created. Rename it from the curriculum list when ready.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to create a module.");
    } finally {
      setBusy(false);
    }
  }

  async function addLesson(module: AdminCurriculumModule) {
    setBusy(true);
    try {
      const position = module.lessons.reduce((highest, lesson) => Math.max(highest, lesson.position), 0) + 1;
      await api.adminCreateLesson(module.id, {
        title: "New lesson",
        slug: `new-lesson-${Date.now().toString(36)}`,
        description: "",
        content_en: "Introduction\nWrite the lesson introduction here.\n\nLearning objectives\n- Add the first objective.\n",
        content_mm: null,
        position,
        duration_minutes: 30,
        status: "draft",
      }, csrf());
      const loaded = await refreshCurriculum();
      const createdModule = loaded.find(item => item.id === module.id);
      const created = createdModule?.lessons.find(lesson => lesson.position === position);
      if (created) await openLesson(created);
      notify("Draft lesson created.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to create a lesson.");
    } finally {
      setBusy(false);
    }
  }

  async function openLesson(lesson: AdminCurriculumLesson) {
    setDraft({ ...lesson });
    setPreview(false);
    setPreviewMyanmar(false);
    setExamples([]);
    setQuiz(null);
    setEditorLoading(true);
    try {
      const [loadedExamples, loadedQuiz] = await Promise.all([
        api.adminExamples(lesson.id).catch(() => []),
        adminQuizApi.get(lesson.id).catch(() => null),
      ]);
      setExamples(loadedExamples);
      setQuiz(loadedQuiz);
    } finally {
      setEditorLoading(false);
    }
  }

  async function saveLesson() {
    if (!draft) return;
    if (draft.title.trim().length < 2) { notify("Lesson title must contain at least 2 characters."); return; }
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(draft.slug)) { notify("Lesson slug must use lowercase letters, numbers, and single hyphens."); return; }
    setBusy(true);
    try {
      await api.adminUpdateLesson(draft.id, {
        title: draft.title.trim(),
        slug: draft.slug,
        description: draft.description,
        content_en: draft.content_en,
        content_mm: draft.content_mm?.trim() ? draft.content_mm : null,
        position: Number(draft.position),
        duration_minutes: Number(draft.duration_minutes),
        status: draft.status,
      }, csrf());
      setCurriculum(current => current.map(module => ({
        ...module,
        lessons: module.lessons.map(lesson => lesson.id === draft.id ? { ...lesson, ...draft, title: draft.title.trim(), position: Number(draft.position), duration_minutes: Number(draft.duration_minutes) } : lesson),
      })));
      notify("Lesson saved.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to save this lesson.");
    } finally {
      setBusy(false);
    }
  }

  async function saveExample(example: AdminCodeExample) {
    if (!example.title.trim()) { notify("Every example needs a title."); return; }
    if (!example.source_code.trim()) { notify("Every example needs source code."); return; }
    setBusy(true);
    try {
      await api.adminUpdateExample(example.id, {
        title: example.title.trim(),
        language: example.language || "c",
        filename: example.filename || null,
        source_code: example.source_code,
        description: example.description,
        position: Number(example.position),
      }, csrf());
      notify(`Saved example: ${example.title}`);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to save this example.");
    } finally {
      setBusy(false);
    }
  }

  async function addExample() {
    if (!draft) return;
    setBusy(true);
    try {
      const position = examples.reduce((highest, example) => Math.max(highest, example.position), 0) + 1;
      const created = await api.adminCreateExample(draft.id, {
        title: "New example",
        language: "c",
        filename: "main.c",
        source_code: "#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello\\n\");\n    return 0;\n}\n",
        description: "Expected output:\nHello",
        position,
      }, csrf());
      setExamples(current => [...current, { id: created.id, title: "New example", language: "c", filename: "main.c", source_code: "#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello\\n\");\n    return 0;\n}\n", description: "Expected output:\nHello", position }]);
      notify("Example created.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to create an example.");
    } finally {
      setBusy(false);
    }
  }

  function updateExample(index: number, patch: Partial<AdminCodeExample>) {
    setExamples(current => current.map((example, itemIndex) => itemIndex === index ? { ...example, ...patch } : example));
  }

  function updateQuestion(index: number, patch: Partial<AdminQuiz["questions"][number]>) {
    setQuiz(current => current ? { ...current, questions: current.questions.map((question, itemIndex) => itemIndex === index ? { ...question, ...patch } : question) } : current);
  }

  async function saveQuestion(index: number) {
    if (!quiz) return;
    const question = quiz.questions[index];
    if (!question.prompt.trim()) { notify("A quiz question needs a prompt."); return; }
    if (question.options.length < 2) { notify("A quiz question needs at least two options."); return; }
    if (!question.options.includes(question.correct_answer)) { notify("The correct answer must be one of the listed options."); return; }
    setBusy(true);
    try {
      const saved = await adminQuizApi.updateQuestion(question.id, {
        prompt: question.prompt.trim(),
        options: question.options.map(option => option.trim()).filter(Boolean),
        correct_answer: question.correct_answer,
        explanation: question.explanation,
        question_type: question.question_type,
        position: Number(question.position),
      }, csrf());
      updateQuestion(index, saved);
      notify(`Saved question ${question.position}.`);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to save this question.");
    } finally {
      setBusy(false);
    }
  }

  async function addQuestion() {
    if (!draft) return;
    setBusy(true);
    try {
      const position = (quiz?.questions.reduce((highest, question) => Math.max(highest, question.position), 0) ?? 0) + 1;
      const created = await adminQuizApi.createQuestion(draft.id, {
        prompt: "New question",
        options: ["Option A", "Option B"],
        correct_answer: "Option A",
        explanation: "Explain why the correct answer is correct.",
        question_type: "multiple_choice",
        position,
      }, csrf());
      setQuiz(current => current ? { ...current, questions: [...current.questions, created] } : { id: null, lesson_id: draft.id, title: "Lesson quiz", explanation: "", questions: [created] });
      notify("Quiz question created.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Unable to create a quiz question.");
    } finally {
      setBusy(false);
    }
  }

  if (!course || !form) return <Card className="p-7">{message || "Loading builder…"}</Card>;

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-indigo-300">Courses / Builder</p>
          <h1 className="mt-2 text-3xl font-bold">{course.title}</h1>
          <p className="mt-2 text-sm text-slate-500">Changes are saved to the server. <Badge>{course.status}</Badge></p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => decide("in_review")} disabled={busy} className="bg-elevated text-slate-200 hover:bg-line">Submit review</Button>
          <Button onClick={() => decide("publish")} disabled={busy} className="bg-success text-white hover:bg-emerald-500">Publish</Button>
          <Button onClick={() => decide("draft")} disabled={busy} className="bg-elevated text-slate-200 hover:bg-line">Unpublish</Button>
        </div>
      </div>

      <div className="mt-8 flex gap-2 overflow-x-auto border-b border-line">
        {["Overview", "Curriculum", "Learning Outcomes", "Requirements", "Media", "SEO", "Settings"].map(item => (
          <button key={item} className={`whitespace-nowrap px-4 py-3 text-sm ${tab === item ? "border-b-2 border-primary text-white" : "text-slate-500 hover:text-slate-300"}`} onClick={() => setTab(item)}>{item}</button>
        ))}
      </div>

      {tab === "Overview" && (
        <Card className="mt-6 space-y-4 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-bold">Course overview</h2>
            <Button onClick={saveCourse} disabled={busy}>Save course</Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Title"><input className={inputClass} value={form.title} onChange={event => setForm({ ...form, title: event.target.value })} /></Field>
            <Field label="Level">
              <select className={inputClass} value={form.level} onChange={event => setForm({ ...form, level: event.target.value })}>
                {["beginner", "intermediate", "advanced"].map(level => <option key={level} value={level}>{level}</option>)}
              </select>
            </Field>
          </div>
          <Field label="Short description" hint="Shown on course cards."><input className={inputClass} value={form.short_description} onChange={event => setForm({ ...form, short_description: event.target.value })} /></Field>
          <Field label="Description"><textarea className={textAreaClass} rows={6} value={form.description} onChange={event => setForm({ ...form, description: event.target.value })} /></Field>
          <Field label="Estimated duration in minutes"><input type="number" min={0} className={inputClass} value={form.estimated_duration} onChange={event => setForm({ ...form, estimated_duration: Number(event.target.value) })} /></Field>
        </Card>
      )}

      {tab === "Curriculum" && (
        <Card className="mt-6 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold">Curriculum</h2>
              <p className="mt-1 text-sm text-slate-500">Select a lesson to edit its content, examples, and quiz.</p>
            </div>
            <Button onClick={addModule} disabled={busy}>Add module</Button>
          </div>
          <div className="mt-6 space-y-4">
            {modules.map(module => (
              <div className="rounded-xl border border-line bg-elevated p-5" key={module.id}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-semibold">Module {module.position}: {module.title}</p>
                  <Button className="bg-surface" onClick={() => addLesson(module)} disabled={busy}>Add lesson</Button>
                </div>
                <div className="mt-3 space-y-2">
                  {module.lessons.length === 0 && <p className="rounded-lg border border-dashed border-line px-4 py-3 text-sm text-slate-500">No lessons in this module yet.</p>}
                  {[...module.lessons].sort((a, b) => a.position - b.position).map(lesson => (
                    <button
                      key={lesson.id}
                      onClick={() => openLesson(lesson)}
                      className={`flex w-full flex-wrap items-center justify-between gap-2 rounded-lg px-4 py-3 text-left text-sm transition ${draft?.id === lesson.id ? "bg-indigo-500/15 text-indigo-200" : "bg-surface text-slate-300 hover:bg-line/60"}`}
                    >
                      <span>{lesson.position}. {lesson.title}</span>
                      <span className="text-xs text-slate-500">{lesson.status} · {lesson.duration_minutes} min</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {draft && (
            <div className="mt-8 rounded-2xl border border-indigo-400/30 bg-ink/60 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-widest text-indigo-300">Editing lesson</p>
                  <h3 className="mt-1 text-lg font-bold">{draft.title}</h3>
                  {selectedModule && <p className="text-xs text-slate-500">{selectedModule.title}</p>}
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button className="bg-elevated text-slate-200 hover:bg-line" onClick={() => setPreview(current => !current)}>{preview ? "Hide preview" : "Preview"}</Button>
                  <Button onClick={saveLesson} disabled={busy}>Save lesson</Button>
                </div>
              </div>

              {editorLoading && <p className="mt-3 text-sm text-slate-500">Loading examples and quiz…</p>}

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <Field label="Title"><input className={inputClass} value={draft.title} onChange={event => setDraft({ ...draft, title: event.target.value })} /></Field>
                <Field label="Slug" hint="Lowercase letters, numbers, hyphens."><input className={inputClass} value={draft.slug} onChange={event => setDraft({ ...draft, slug: event.target.value })} /></Field>
                <Field label="Status">
                  <select className={inputClass} value={draft.status} onChange={event => setDraft({ ...draft, status: event.target.value })}>
                    {["draft", "published"].map(status => <option key={status} value={status}>{status}</option>)}
                  </select>
                </Field>
                <Field label="Position"><input type="number" min={0} className={inputClass} value={draft.position} onChange={event => setDraft({ ...draft, position: Number(event.target.value) })} /></Field>
                <Field label="Duration in minutes"><input type="number" min={0} className={inputClass} value={draft.duration_minutes} onChange={event => setDraft({ ...draft, duration_minutes: Number(event.target.value) })} /></Field>
                <Field label="Short description"><input className={inputClass} value={draft.description} onChange={event => setDraft({ ...draft, description: event.target.value })} /></Field>
              </div>
              <Field label="English content" hint="Supports headings, lists, fenced C code, expected output, exercises, and solutions.">
                <textarea className={`${textAreaClass} min-h-80`} value={draft.content_en} onChange={event => setDraft({ ...draft, content_en: event.target.value })} />
              </Field>
              <Field label="Myanmar content">
                <textarea className={`${textAreaClass} min-h-48`} value={draft.content_mm ?? ""} onChange={event => setDraft({ ...draft, content_mm: event.target.value })} />
              </Field>

              {preview && (
                <div className="mt-5 rounded-xl border border-line bg-surface p-5">
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-200">Live preview</p>
                    <Button className="bg-elevated text-slate-200 hover:bg-line" onClick={() => setPreviewMyanmar(current => !current)}>{previewMyanmar ? "Show English" : "Show Myanmar"}</Button>
                  </div>
                  {previewMyanmar
                    ? <LessonContent content={draft.content_mm || "Myanmar explanation is not available for this lesson yet."} />
                    : <LessonContent content={draft.content_en} />}
                </div>
              )}

              <section className="mt-8" aria-labelledby="admin-examples-heading">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h4 id="admin-examples-heading" className="font-bold">Code examples</h4>
                  <Button className="bg-elevated text-slate-200 hover:bg-line" onClick={addExample} disabled={busy}>Add example</Button>
                </div>
                <div className="mt-3 space-y-4">
                  {examples.map((example, index) => (
                    <div className="rounded-xl border border-line bg-surface p-4" key={example.id}>
                      <div className="grid gap-3 md:grid-cols-4">
                        <Field label="Title"><input className={inputClass} value={example.title} onChange={event => updateExample(index, { title: event.target.value })} /></Field>
                        <Field label="Language"><input className={inputClass} value={example.language} onChange={event => updateExample(index, { language: event.target.value })} /></Field>
                        <Field label="Filename"><input className={inputClass} value={example.filename ?? ""} onChange={event => updateExample(index, { filename: event.target.value })} /></Field>
                        <Field label="Position"><input type="number" min={0} className={inputClass} value={example.position} onChange={event => updateExample(index, { position: Number(event.target.value) })} /></Field>
                      </div>
                      <Field label="Source code"><textarea className={`${textAreaClass} min-h-40`} value={example.source_code} onChange={event => updateExample(index, { source_code: event.target.value })} /></Field>
                      <Field label="Description and expected output"><textarea className={`${textAreaClass} min-h-24`} value={example.description} onChange={event => updateExample(index, { description: event.target.value })} /></Field>
                      <Button className="mt-3" onClick={() => saveExample(example)} disabled={busy}>Save example</Button>
                    </div>
                  ))}
                  {examples.length === 0 && <p className="rounded-lg border border-dashed border-line px-4 py-3 text-sm text-slate-500">No code examples yet.</p>}
                </div>
              </section>

              <section className="mt-8" aria-labelledby="admin-quiz-heading">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h4 id="admin-quiz-heading" className="font-bold">Quiz</h4>
                    {quiz && <p className="text-xs text-slate-500">{quiz.title} · {quiz.questions.length} questions</p>}
                  </div>
                  <Button className="bg-elevated text-slate-200 hover:bg-line" onClick={addQuestion} disabled={busy}>Add question</Button>
                </div>
                <div className="mt-3 space-y-4">
                  {quiz?.questions.map((question, index) => (
                    <div className="rounded-xl border border-line bg-surface p-4" key={question.id}>
                      <div className="grid gap-3 md:grid-cols-3">
                        <Field label="Prompt"><input className={inputClass} value={question.prompt} onChange={event => updateQuestion(index, { prompt: event.target.value })} /></Field>
                        <Field label="Type">
                          <select className={inputClass} value={question.question_type} onChange={event => updateQuestion(index, { question_type: event.target.value })}>
                            {["multiple_choice", "true_false", "code_output"].map(type => <option key={type} value={type}>{type}</option>)}
                          </select>
                        </Field>
                        <Field label="Position"><input type="number" min={1} className={inputClass} value={question.position} onChange={event => updateQuestion(index, { position: Number(event.target.value) })} /></Field>
                      </div>
                      <div className="grid gap-3 md:grid-cols-2">
                        <Field label="Options" hint="One option per line."><textarea className={`${textAreaClass} min-h-24`} value={question.options.join("\n")} onChange={event => updateQuestion(index, { options: splitLines(event.target.value) })} /></Field>
                        <div>
                          <Field label="Correct answer">
                            <select className={inputClass} value={question.correct_answer} onChange={event => updateQuestion(index, { correct_answer: event.target.value })}>
                              {question.options.map(option => <option key={option} value={option}>{option}</option>)}
                            </select>
                          </Field>
                          <Field label="Explanation"><textarea className={`${textAreaClass} min-h-16`} value={question.explanation} onChange={event => updateQuestion(index, { explanation: event.target.value })} /></Field>
                        </div>
                      </div>
                      <Button className="mt-3" onClick={() => saveQuestion(index)} disabled={busy}>Save question</Button>
                    </div>
                  ))}
                  {!quiz?.questions.length && <p className="rounded-lg border border-dashed border-line px-4 py-3 text-sm text-slate-500">No quiz questions yet.</p>}
                </div>
              </section>
            </div>
          )}
        </Card>
      )}

      {tab === "Learning Outcomes" && (
        <Card className="mt-6 p-6">
          <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Learning outcomes</h2><Button onClick={saveCourse} disabled={busy}>Save course</Button></div>
          <Field label="One outcome per line"><textarea className={`${textAreaClass} min-h-48`} value={form.outcomes.join("\n")} onChange={event => setForm({ ...form, outcomes: splitLines(event.target.value) })} /></Field>
        </Card>
      )}

      {tab === "Requirements" && (
        <Card className="mt-6 p-6">
          <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Requirements</h2><Button onClick={saveCourse} disabled={busy}>Save course</Button></div>
          <Field label="One requirement per line"><textarea className={`${textAreaClass} min-h-48`} value={form.requirements.join("\n")} onChange={event => setForm({ ...form, requirements: splitLines(event.target.value) })} /></Field>
        </Card>
      )}

      {tab === "Media" && (
        <Card className="mt-6 p-6">
          <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Media</h2><Button onClick={saveCourse} disabled={busy}>Save course</Button></div>
          <Field label="Thumbnail URL"><input className={inputClass} value={form.thumbnail ?? ""} onChange={event => setForm({ ...form, thumbnail: event.target.value || null })} /></Field>
        </Card>
      )}

      {tab === "SEO" && (
        <Card className="mt-6 space-y-4 p-6">
          <div className="flex items-center justify-between"><h2 className="text-xl font-bold">SEO</h2><Button onClick={saveCourse} disabled={busy}>Save course</Button></div>
          <Field label="Slug"><input className={inputClass} value={form.slug} onChange={event => setForm({ ...form, slug: event.target.value })} /></Field>
          <Field label="Short description"><textarea className={textAreaClass} value={form.short_description} onChange={event => setForm({ ...form, short_description: event.target.value })} /></Field>
        </Card>
      )}

      {tab === "Settings" && (
        <Card className="mt-6 space-y-4 p-6">
          <h2 className="text-xl font-bold">Publishing settings</h2>
          <p className="text-sm text-slate-400">Publishing requires a platform administrator. Instructors can save lessons and submit the course for review.</p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => decide("in_review")} disabled={busy} className="bg-elevated text-slate-200 hover:bg-line">Submit review</Button>
            <Button onClick={() => decide("publish")} disabled={busy} className="bg-success text-white hover:bg-emerald-500">Publish</Button>
            <Button onClick={() => decide("draft")} disabled={busy} className="bg-elevated text-slate-200 hover:bg-line">Unpublish</Button>
          </div>
        </Card>
      )}

      {message && <p className="mt-4 rounded-lg border border-line bg-surface px-4 py-3 text-sm text-slate-300" role="status">{message}</p>}
    </div>
  );
}
