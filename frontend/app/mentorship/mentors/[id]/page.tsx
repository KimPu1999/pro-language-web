import { MentorDetail } from "@/components/career-pages";
export default async function Page({params}:{params:Promise<{id:string}>}){return <MentorDetail id={(await params).id}/>;}
