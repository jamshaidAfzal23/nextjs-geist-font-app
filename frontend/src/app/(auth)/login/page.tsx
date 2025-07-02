import { AuthCard } from '@/components/auth/AuthCard'
import { LoginForm } from '@/components/auth/LoginForm'

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <AuthCard
        title="Welcome back"
        description="Enter your credentials to access your account"
        footerText="Don't have an account?"
        footerLink="/signup"
        footerLinkText="Sign up"
      >
        <LoginForm />
      </AuthCard>
    </div>
  )
}