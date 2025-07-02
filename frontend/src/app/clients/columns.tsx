'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Button } from '@/components/ui/button'
import { Icons } from '@/components/ui/icons'
import Link from 'next/link'

export type Client = {
  id: string
  name: string
  contact: string
  email: string
  status: string
  projects: number
}

export const columns: ColumnDef<Client>[] = [
  {
    accessorKey: 'name',
    header: 'Client Name',
  },
  {
    accessorKey: 'contact',
    header: 'Contact Person',
  },
  {
    accessorKey: 'email',
    header: 'Email',
  },
  {
    accessorKey: 'status',
    header: 'Status',
  },
  {
    accessorKey: 'projects',
    header: 'Projects',
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const client = row.original

      return (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/clients/${client.id}`}>
              <Icons.eye className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="ghost" size="sm">
            <Icons.edit className="h-4 w-4" />
          </Button>
        </div>
      )
    },
  },
]