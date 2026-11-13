import { TeamDetail } from "@/components/collaboration-pages";
export default async function Page({params}:{params:Promise<{teamId:string}>}){return <TeamDetail id={(await params).teamId}/>;}
