export type Language = { id: string; name: string; slug: string; color: string };
export type Course = { id: string; title: string; slug: string; description: string; level: string; category: string; duration_minutes: number; language: Language; outcomes: string[]; module_count?: number };
export type Lesson = { id: string; title: string; slug: string; content_en: string; content_mm?: string | null; order_index: number; code_examples: { id: string; title: string; language: string; code: string }[] };
export type Module = { id: string; title: string; order_index: number; lessons: Lesson[] };
export type CourseDetail = Course & { modules: Module[] };
export type Paginated<T> = { items: T[]; page: number; page_size: number; total: number; pages: number };
