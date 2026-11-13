import { CareerPath } from "@/components/career-pages";
export default async function Page({params}:{params:Promise<{slug:string}>}){return <CareerPath slug={(await params).slug}/>;}
