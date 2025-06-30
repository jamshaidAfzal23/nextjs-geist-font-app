/**
 * Authentication Context for Smart CRM SaaS application.
 * This module provides authentication state management and user session handling
 * throughout the application using React Context API.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { User, UserLogin, UserToken } from '@/types/api';

// Authentication context type definition
interface AuthContextType {
  // State
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  
  // Actions
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// Create the authentication context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Props for the AuthProvider component
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication Provider component that wraps the application
 * and provides authentication state and methods to all child components.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  // State management
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Computed state
  const isAuthenticated = !!user && apiClient.isAuthenticated();

  /**
   * Initialize authentication state on component mount.
   * Checks for existing token and validates user session.
   */
  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Initialize authentication by checking for existing token
   * and validating the user session.
   */
  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Check if there's a stored token
      if (apiClient.isAuthenticated()) {
        // Try to fetch current user to validate token
        await refreshUser();
      }
    } catch (error) {
      console.error('Failed to initialize authentication:', error);
      // Clear invalid token
      apiClient.clearToken();
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login user with email and password.
   * Sets user state and redirects to dashboard on success.
   */
  const login = async (credentials: UserLogin): Promise<void> => {
    try {
      setIsLoading(true);
      
      // Authenticate with API
      const tokenData: UserToken = await apiClient.login(credentials);
      
      // Set user state
      setUser(tokenData.user);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error; // Re-throw to allow component to handle error display
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout user and clear all authentication state.
   * Redirects to login page.
   */
  const logout = () => {
    // Clear API client token
    apiClient.logout();
    
    // Clear user state
    setUser(null);
    
    // Redirect to login page
    router.push('/login');
  };

  /**
   * Refresh user data from the API.
   * Useful for updating user information after profile changes.
   */
  const refreshUser = async (): Promise<void> => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // Token is invalid, clear authentication
      apiClient.clearToken();
      setUser(null);
      throw error;
    }
  };

  // Context value
  const contextValue: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to use the authentication context.
 * Provides easy access to authentication state and methods.
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Higher-order component to protect routes that require authentication.
 * Redirects to login page if user is not authenticated.
 */
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.ComponentType<P> {
  const AuthenticatedComponent = (props: P) => {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login');
      }
    }, [isAuthenticated, isLoading, router]);

    // Show loading spinner while checking authentication
    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    // Don't render component if not authenticated
    if (!isAuthenticated) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };

  // Set display name for debugging
  AuthenticatedComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name})`;

  return AuthenticatedComponent;
}

/**
 * Hook to check if user has specific role permissions.
 */
export function usePermissions() {
  const { user } = useAuth();

  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  const hasAnyRole = (roles: string[]): boolean => {
    return user ? roles.includes(user.role) : false;
  };

  const isAdmin = (): boolean => {
    return hasRole('admin');
  };

  const isManager = (): boolean => {
    return hasAnyRole(['admin', 'manager']);
  };

  const canManageUsers = (): boolean => {
    return hasAnyRole(['admin', 'manager']);
  };

  const canManageClients = (): boolean => {
    return hasAnyRole(['admin', 'manager', 'developer']);
  };

  const canManageProjects = (): boolean => {
    return hasAnyRole(['admin', 'manager', 'developer']);
  };

  const canViewFinancials = (): boolean => {
    return hasAnyRole(['admin', 'manager']);
  };

  const canManageFinancials = (): boolean => {
    return hasAnyRole(['admin', 'manager']);
  };

  return {
    user,
    hasRole,
    hasAnyRole,
    isAdmin,
    isManager,
    canManageUsers,
    canManageClients,
    canManageProjects,
    canViewFinancials,
    canManageFinancials,
  };
}
