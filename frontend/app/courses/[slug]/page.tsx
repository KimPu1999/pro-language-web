import Link from "next/link";
import { notFound } from "next/navigation";
import { BookOpen, Clock, ListChecks } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Card } from "@/components/ui";
import { EnrollButton } from "@/components/enroll-button";
import { StartLearningButton } from "@/components/start-learning-button";

export default async function CoursePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let course;
  try { course = await api.course(slug); } catch { notFound(); }
  const lessons = course.modules.flatMap(module => module.lessons);
  const exampleCount = lessons.reduce((count, lesson) => count + lesson.code_examples.length, 0);
  const requirements = course.requirements ?? [];
  let related = [] as typeof course[];
  try {
    const page = await api.courses(`?page_size=12&category=${encodeURIComponent(course.category.slug)}`);
    related = page.items.filter(item => item.slug !== course.slug).slice(0, 3) as typeof related;
  } catch { /* Optional section. */ }
  return <section className="mx-auto max-w-6xl px-5 py-14 lg:px-8">
    <Link className="text-sm text-indigo-300" href="/courses">← All courses</Link>
    <div className="mt-8 grid gap-10 lg:grid-cols-[1fr_320px]"><div>
      <Badge>{course.language.name} · {course.level} · Free</Badge><h1 className="mt-5 text-4xl font-extrabold tracking-tight sm:text-5xl">{course.title}</h1><p className="mt-5 text-lg leading-8 text-slate-400">{course.description}</p>
      <div className="mt-7 flex flex-wrap gap-5 text-sm text-slate-400"><span><Clock className="mr-2 inline" size={16}/>{course.duration_minutes ? `${Math.round(course.duration_minutes / 60)} hours` : "Editorial estimate pending"}</span><span><ListChecks className="mr-2 inline" size={16}/>{course.modules.length} modules</span><span><BookOpen className="mr-2 inline" size={16}/>{lessons.length} lessons · {exampleCount} examples</span></div>
      <h2 className="mt-14 text-2xl font-bold">What you’ll learn</h2><ul className="mt-5 grid gap-3 sm:grid-cols-2">{course.outcomes.map(outcome => <li className="rounded-xl bg-surface p-4 text-sm text-slate-300" key={outcome}>✓ {outcome}</li>)}</ul>
      {requirements.length > 0 && <><h2 className="mt-14 text-2xl font-bold">Prerequisites</h2><ul className="mt-5 space-y-2 text-sm text-slate-400">{requirements.map(requirement => <li key={requirement}>• {requirement}</li>)}</ul></>}
      <h2 className="mt-14 text-2xl font-bold">Curriculum</h2>{course.status === "curriculum_pending" && <Card className="mt-5 border-amber-400/20 p-5 text-amber-200">This course overview is available now. The reviewed curriculum is still being authored.</Card>}<div className="mt-5 space-y-3">{course.modules.map(module => <Card className="p-5" key={module.id}><h3 className="font-semibold">{module.order_index}. {module.title}</h3><p className="mt-2 text-sm text-slate-500">{module.lessons.length} lessons</p><div className="mt-4 space-y-2">{module.lessons.map(lesson => <Link className="block rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-white/5 hover:text-white" href={`/courses/${course.slug}/learn/${lesson.slug}`} key={lesson.id}>{lesson.order_index}. {lesson.title}<span className="float-right text-xs text-slate-600">{lesson.duration_minutes} min</span></Link>)}</div></Card>)}</div>{!course.modules.length && <Card className="mt-5 p-6 text-slate-400">Lessons are not available yet. Check back after the curriculum review is complete.</Card>}
      {related.length > 0 && <><h2 className="mt-14 text-2xl font-bold">Related courses</h2><div className="mt-5 grid gap-4 sm:grid-cols-3">{related.map(item => <Link href={`/courses/${item.slug}`} key={item.id}><Card className="h-full p-4 hover:border-indigo-400/50"><Badge>{item.language.name}</Badge><h3 className="mt-3 font-semibold">{item.title}</h3><p className="mt-2 line-clamp-2 text-sm text-slate-500">{item.description}</p></Card></Link>)}</div></>}
    </div><aside><Card className="sticky top-24 p-5"><p className="text-sm text-slate-400">{lessons.length ? "Ready to begin?" : "Course overview"}</p><div className="mt-4">{lessons[0] ? <StartLearningButton courseSlug={course.slug} lessonSlug={lessons[0].slug}/> : <EnrollButton slug={course.slug}/>}</div>{lessons[0] && <p className="mt-3 text-center text-xs text-slate-500">Your enrollment and progress are saved to your account.</p>}</Card></aside></div>
  </section>;
}
