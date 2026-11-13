import{notFound}from"next/navigation";import{projectApi}from"@/lib/project-api";import{ProjectDetail}from"@/components/project-detail";
export default async function ProjectPage({params}:{params:Promise<{slug:string}>}){const{slug}=await params;try{return <section className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><ProjectDetail project={await projectApi.detail(slug)}/></section>}catch{notFound()}}
