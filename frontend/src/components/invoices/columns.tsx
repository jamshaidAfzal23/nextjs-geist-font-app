import { ColumnDef } from "@tanstack/react-table";
import { Invoice } from "@/types";
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
import { formatCurrency } from "@/lib/utils";

export const columns: ColumnDef<Invoice>[] = [
  {
    accessorKey: "id",
    header: "Invoice ID",
  },
  {
    accessorKey: "client",
    header: "Client",
  },
  {
    accessorKey: "amount",
    header: "Amount",
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue("amount"));
      return formatCurrency(amount);
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status");
      const variant = {
        paid: "default",
        pending: "secondary",
        overdue: "destructive",
      }[status as string] as "default" | "secondary" | "destructive";

      return (
        <Badge variant={variant} className="capitalize">
          {status as string}
        </Badge>
      );
    },
  },
  {
    accessorKey: "date",
    header: "Date",
    cell: ({ row }) => {
      const date = new Date(row.getValue("date"));
      return date.toLocaleDateString();
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
      const invoice = row.original;

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
            <Link href={`/finance/invoices/${invoice.id}`}>
              <DropdownMenuItem>View</DropdownMenuItem>
            </Link>
            <Link href={`/finance/invoices/${invoice.id}/edit`}>
              <DropdownMenuItem>Edit</DropdownMenuItem>
            </Link>
            <DropdownMenuItem>Send to Client</DropdownMenuItem>
            <DropdownMenuItem>Download PDF</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];