import { Leaderboard } from "@/components/collaboration-pages";
export default async function Page({params}:{params:Promise<{slug:string}>}){return <Leaderboard slug={(await params).slug}/>;}
