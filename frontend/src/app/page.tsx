/**
 * Root page for Smart CRM SaaS application.
 * Handles redirection based on authentication status.
 * Authenticated users are redirected to dashboard,
 * unauthenticated users are redirected to login.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/AuthProvider';
import { PageLoading } from '@/components/ui/loading';

/**
 * Root page component that handles authentication-based redirection.
 */
export default function RootPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for authentication state to be determined
    if (!isLoading) {
      // Redirect based on authentication status
      if (isAuthenticated) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while determining authentication
  return (
    <PageLoading message="Initializing Smart CRM..." />
  );
}
