import { LessonContent } from "./lesson-content";
export function BilingualLessonContent({ english }: { english: string; myanmar?: string|null }) { return <LessonContent content={english}/>; }
