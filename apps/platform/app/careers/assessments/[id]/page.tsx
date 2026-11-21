import { AssessmentDetailPage } from "@/components/careers-hub";
export default async function AssessmentDetailRoute({ params }: { params: Promise<{ id: string }> }) { return <AssessmentDetailPage id={(await params).id} />; }
