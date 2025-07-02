import { DataTable } from '@/components/data-table/DataTable'
import { columns } from './columns'
import { MainNav } from '@/components/navigation/MainNav'
import { Button } from '@/components/ui/button'
import { Icons } from '@/components/ui/icons'
import Link from 'next/link'

async function getClients() {
  // Replace with actual API call
  return [
    {
      id: '1',
      name: 'Acme Inc',
      contact: 'Jane Smith',
      email: 'jane@acme.com',
      status: 'Active',
      projects: 3,
    },
    // More clients...
  ]
}

export default async function ClientsPage() {
  const clients = await getClients()

  return (
    <div className="flex flex-col">
      <MainNav />
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Clients</h2>
          <Button asChild>
            <Link href="/clients/new">
              <Icons.plus className="mr-2 h-4 w-4" />
              Add Client
            </Link>
          </Button>
        </div>
        <DataTable columns={columns} data={clients} />
      </div>
    </div>
  )
}