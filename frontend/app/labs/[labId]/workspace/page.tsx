import { LabWorkspace } from "@/components/lab-pages";export default async function Page({params}:{params:Promise<{labId:string}>}){return <LabWorkspace id={(await params).labId}/>}
