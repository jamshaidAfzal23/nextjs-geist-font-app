import { DataTable } from "@/components/invoices/data-table";
import { columns } from "@/components/invoices/columns";
import { DashboardShell } from "@/components/shell";
import { DashboardHeader } from "@/components/header";
import { Invoice } from "@/types";
import { Button } from "@/components/ui/button";
import Link from "next/link";

async function getInvoices(): Promise<Invoice[]> {
  // Replace with actual API call
  return [
    {
      id: "INV-001",
      client: "Acme Inc.",
      amount: 1250.0,
      status: "paid",
      date: new Date(Date.now() - 86400000 * 7).toISOString(),
      dueDate: new Date(Date.now() - 86400000 * 3).toISOString(),
    },
    {
      id: "INV-002",
      client: "Globex Corporation",
      amount: 3250.5,
      status: "pending",
      date: new Date(Date.now() - 86400000 * 14).toISOString(),
      dueDate: new Date(Date.now() + 86400000 * 7).toISOString(),
    },
    // Add more mock invoices as needed
  ];
}

export default async function InvoicesPage() {
  const invoices = await getInvoices();

  return (
    <DashboardShell>
      <DashboardHeader
        heading="Invoices"
        text="Manage and track your invoices"
      >
        <div className="flex gap-2">
          <Button variant="outline">Export</Button>
          <Link href="/finance/invoices/new">
            <Button>Create Invoice</Button>
          </Link>
        </div>
      </DashboardHeader>
      <div className="overflow-hidden rounded-md border bg-background">
        <DataTable columns={columns} data={invoices} />
      </div>
    </DashboardShell>
  );
}