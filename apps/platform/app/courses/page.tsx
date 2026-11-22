import { Suspense } from "react";
import { CourseCatalog } from "@/components/course-catalog";

export default function CoursesPage() {
  return (
    <Suspense fallback={<div className="mx-auto min-h-[50vh] max-w-6xl px-6 py-16 text-muted">Loading courses…</div>}>
      <CourseCatalog />
    </Suspense>
  );
}
