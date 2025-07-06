import { AuthCard } from '@/components/auth/auth-card'
import { SignupForm } from '@/components/auth/signup-form'

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <AuthCard
        title="Create an account"
        description="Enter your information to get started"
        footerText="Already have an account?"
        footerLink="/login"
        footerLinkText="Sign in"
      >
        <SignupForm />
      </AuthCard>
    </div>
  )
}