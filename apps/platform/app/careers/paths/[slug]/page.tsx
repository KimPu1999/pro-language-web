import { CareerPathPage } from "@/components/careers-hub";
export default async function CareerPathRoute({ params }: { params: Promise<{ slug: string }> }) { return <CareerPathPage slug={(await params).slug} />; }
