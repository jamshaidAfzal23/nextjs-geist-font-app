import { DataTable } from "@/components/projects/data-table";
import { columns } from "@/components/projects/columns";
import { DashboardShell } from "@/components/shell";
import { DashboardHeader } from "@/components/header";
import { Project } from "@/types";
import { Button } from "@/components/ui/button";
import Link from "next/link";

async function getProjects(): Promise<Project[]> {
  // Replace with actual API call
  return [
    {
      id: "1",
      name: "Website Redesign",
      client: "Acme Inc.",
      status: "in-progress",
      dueDate: new Date(Date.now() + 86400000 * 7).toISOString(),
      priority: "high",
      progress: 65,
    },
    {
      id: "2",
      name: "Mobile App Development",
      client: "Globex Corporation",
      status: "planning",
      dueDate: new Date(Date.now() + 86400000 * 14).toISOString(),
      priority: "medium",
      progress: 20,
    },
    // Add more mock projects as needed
  ];
}

export default async function ProjectsPage() {
  const projects = await getProjects();

  return (
    <DashboardShell>
      <DashboardHeader
        heading="Projects"
        text="Manage your projects and track progress"
      >
        <Link href="/projects/new">
          <Button>New Project</Button>
        </Link>
      </DashboardHeader>
      <div className="overflow-hidden rounded-md border bg-background">
        <DataTable columns={columns} data={projects} />
      </div>
    </DashboardShell>
  );
}