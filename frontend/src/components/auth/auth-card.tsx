import { Button } from '@/components/ui/button'
import Link from 'next/link'

interface AuthCardProps {
  title: string
  description: string
  children: React.ReactNode
  footerText: string
  footerLink: string
  footerLinkText: string
}

export function AuthCard({
  title,
  description,
  children,
  footerText,
  footerLink,
  footerLinkText,
}: AuthCardProps) {
  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md dark:bg-gray-850">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="text-gray-500 dark:text-gray-400">{description}</p>
      </div>
      {children}
      <div className="text-center text-sm">
        {footerText}{' '}
        <Button variant="link" className="px-0" asChild>
          <Link href={footerLink}>{footerLinkText}</Link>
        </Button>
      </div>
    </div>
  )
}