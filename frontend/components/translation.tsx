import { LessonContent } from "./lesson-content";
export function BilingualLessonContent({ english, myanmar, locale = "en" }: { english: string; myanmar?: string|null; locale?: "en" | "my" }) {
  const content = locale === "my" && myanmar?.trim() ? myanmar : english;
  return <LessonContent content={content}/>;
}
