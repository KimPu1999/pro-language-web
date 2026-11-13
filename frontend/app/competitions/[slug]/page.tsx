import { CompetitionDetail } from "@/components/collaboration-pages";
export default async function Page({params}:{params:Promise<{slug:string}>}){return <CompetitionDetail slug={(await params).slug}/>;}
