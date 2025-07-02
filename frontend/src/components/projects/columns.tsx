import { ColumnDef } from "@tanstack/react-table";
import { Project } from "@/types";
import { Button } from "@/components/ui/button";
import { ArrowUpDown, MoreHorizontal } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export const columns: ColumnDef<Project>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Project Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: "client",
    header: "Client",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status");
      const variant = {
        planning: "secondary",
        "in-progress": "default",
        completed: "outline",
        blocked: "destructive",
      }[status as string] as "secondary" | "default" | "outline" | "destructive";

      return (
        <Badge variant={variant} className="capitalize">
          {status as string}
        </Badge>
      );
    },
  },
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => {
      const priority = row.getValue("priority");
      const variant = {
        low: "secondary",
        medium: "default",
        high: "destructive",
      }[priority as string] as "secondary" | "default" | "destructive";

      return (
        <Badge variant={variant} className="capitalize">
          {priority as string}
        </Badge>
      );
    },
  },
  {
    accessorKey: "progress",
    header: "Progress",
    cell: ({ row }) => {
      const progress = parseFloat(row.getValue("progress"));
      return (
        <div className="flex items-center gap-2">
          <Progress value={progress} className="h-2" />
          <span>{progress}%</span>
        </div>
      );
    },
  },
  {
    accessorKey: "dueDate",
    header: "Due Date",
    cell: ({ row }) => {
      const date = new Date(row.getValue("dueDate"));
      return date.toLocaleDateString();
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const project = row.original;

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <Link href={`/projects/${project.id}`}>
              <DropdownMenuItem>View Project</DropdownMenuItem>
            </Link>
            <Link href={`/projects/${project.id}/edit`}>
              <DropdownMenuItem>Edit</DropdownMenuItem>
            </Link>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];