import{SecurityDashboard}from"@/components/security-pages";export default async function Page({params}:{params:Promise<{slug:string}>}){return <SecurityDashboard slug={(await params).slug}/>}
