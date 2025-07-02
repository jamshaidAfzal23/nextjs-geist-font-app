import { DataTable } from '@/components/data-table/DataTable'
import { columns } from './columns'
import { MainNav } from '@/components/navigation/MainNav'
import { Button } from '@/components/ui/button'
import { Icons } from '@/components/ui/icons'
import Link from 'next/link'

async function getUsers() {
  // Replace with actual API call
  return [
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Admin',
      status: 'Active',
      lastLogin: '2023-05-15T10:30:00Z',
    },
    // More users...
  ]
}

export default async function UsersPage() {
  const users = await getUsers()

  return (
    <div className="flex flex-col">
      <MainNav />
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">User Management</h2>
          <Button asChild>
            <Link href="/admin/users/new">
              <Icons.plus className="mr-2 h-4 w-4" />
              Add User
            </Link>
          </Button>
        </div>
        <DataTable columns={columns} data={users} />
      </div>
    </div>
  )
}