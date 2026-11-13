import { HackathonDetail } from "@/components/collaboration-pages";
export default async function Page({params}:{params:Promise<{slug:string}>}){return <HackathonDetail slug={(await params).slug}/>;}
