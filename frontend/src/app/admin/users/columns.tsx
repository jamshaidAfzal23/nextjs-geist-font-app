'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Button } from '@/components/ui/button'
import { Icons } from '@/components/ui/icons'
import Link from 'next/link'

export type User = {
  id: string
  name: string
  email: string
  role: string
  status: string
  lastLogin: string
}

export const columns: ColumnDef<User>[] = [
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'email',
    header: 'Email',
  },
  {
    accessorKey: 'role',
    header: 'Role',
  },
  {
    accessorKey: 'status',
    header: 'Status',
  },
  {
    accessorKey: 'lastLogin',
    header: 'Last Login',
    cell: ({ row }) => {
      const date = new Date(row.getValue('lastLogin'))
      return date.toLocaleString()
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const user = row.original

      return (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/admin/users/${user.id}`}>
              <Icons.edit className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="ghost" size="sm">
            <Icons.trash className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      )
    },
  },
]