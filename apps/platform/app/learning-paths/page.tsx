import { redirect } from "next/navigation";

// Keep the historical public URL working while preserving the canonical career-path route.
export default function LearningPathsAlias() {
  redirect("/careers/paths");
}
