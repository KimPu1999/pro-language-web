import Link from "next/link";

const sections = [{ label: "Basic Information", key: "basic" }, { label: "Curriculum", key: "curriculum" }, { label: "Lessons", key: "lessons" }, { label: "Assessments", key: "assessments" }, { label: "Projects", key: "projects" }, { label: "Card Appearance", key: "appearance" }, { label: "Media & Resources", key: "media" }, { label: "Translations", key: "translations" }, { label: "Instructors", key: "instructors" }, { label: "Publishing", key: "publishing" }, { label: "Students & Progress", key: "students" }, { label: "Analytics", key: "analytics" }, { label: "Settings", key: "settings" }];

export function CourseEditorNav({ courseId }: { courseId: string }) {
  return <nav aria-label="Course editor sections" className="flex gap-1 overflow-x-auto rounded-xl border border-line bg-surface p-1">{sections.map(section => <Link key={section.key} href={`/courses/${courseId}?section=${section.key}`} className="whitespace-nowrap rounded-lg px-3 py-2 text-xs font-medium text-muted transition hover:bg-surface-hover hover:text-foreground">{section.label}</Link>)}</nav>;
}
