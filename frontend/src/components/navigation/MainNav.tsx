'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Icons } from '@/components/ui/icons'
import { Button } from '@/components/ui/button'
import { UserNav } from './UserNav'
import { useAuth } from '@/providers/AuthProvider'

export function MainNav() {
  const pathname = usePathname()
  const { user } = useAuth()

  const navItems = [
    {
      href: '/dashboard',
      title: 'Dashboard',
      icon: <Icons.dashboard className="h-4 w-4" />,
    },
    {
      href: '/clients',
      title: 'Clients',
      icon: <Icons.clients className="h-4 w-4" />,
    },
    {
      href: '/projects',
      title: 'Projects',
      icon: <Icons.projects className="h-4 w-4" />,
    },
    {
      href: '/finance/invoices',
      title: 'Finance',
      icon: <Icons.finance className="h-4 w-4" />,
    },
  ]

  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4">
        <nav className="flex items-center space-x-6 mx-6">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'text-sm font-medium transition-colors hover:text-primary',
                pathname.startsWith(item.href)
                  ? 'text-black dark:text-white'
                  : 'text-muted-foreground'
              )}
            >
              <div className="flex items-center gap-2">
                {item.icon}
                {item.title}
              </div>
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center space-x-4">
          {user && <UserNav user={user} />}
        </div>
      </div>
    </div>
  )
}