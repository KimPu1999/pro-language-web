import { notFound } from "next/navigation";
import SectionPage from "@/components/section-page";

const supportedSections = new Set(["about", "contact", "privacy", "terms", "courses", "projects", "challenges", "careers"]);

export default async function SectionRoute({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  if (!supportedSections.has(section)) notFound();
  return <SectionPage section={section} />;
}
