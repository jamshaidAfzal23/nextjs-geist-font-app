/**
 * Main Layout component for Smart CRM SaaS application.
 * Provides the overall application structure including navigation,
 * sidebar, and content areas for authenticated users.
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/providers/AuthProvider';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Users,
  Building2,
  FolderOpen,
  CreditCard,
  Receipt,
  FileText,
  BarChart3,
  Settings,
  Menu,
  X,
  LogOut,
  User,
  Bell,
} from 'lucide-react';

// Navigation item interface
interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  permissions?: string[];
}

// Main navigation items
const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    description: 'Overview and analytics',
  },
  {
    name: 'Clients',
    href: '/clients',
    icon: Building2,
    description: 'Manage client relationships',
    permissions: ['Admin', 'Bidder'],
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderOpen,
    description: 'Track project progress',
    permissions: ['Admin', 'Bidder', 'Developer'],
  },
  {
    name: 'Payments',
    href: '/payments',
    icon: CreditCard,
    description: 'Payment management',
    permissions: ['Admin', 'Finance'],
  },
  {
    name: 'Expenses',
    href: '/expenses',
    icon: Receipt,
    description: 'Expense tracking',
    permissions: ['Admin', 'Finance'],
  },
  {
    name: 'Invoices',
    href: '/invoices',
    icon: FileText,
    description: 'Invoice management',
    permissions: ['Admin', 'Finance'],
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users,
    description: 'User management',
    permissions: ['Admin'],
  },
];

// Main layout props
interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * Main layout component that provides the application structure.
 * Includes sidebar navigation, header, and main content area.
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const pathname = usePathname();

  // Filter navigation items based on user permissions
  const filteredNavItems = navigationItems.filter((item) => {
    if (!item.permissions) return true;
    return user && item.permissions.includes(user.role);
  });

  // Check if current path is active
  const isActivePath = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-white shadow-lg transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Sidebar header */}
        <div className="flex h-16 items-center justify-between px-6 border-b">
          <h1 className="text-xl font-bold text-gray-900">Smart CRM</h1>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = isActivePath(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0',
                    isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                  )}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="border-t p-4">
          <Link
            href="/settings"
            className="group flex items-center rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900"
          >
            <Settings className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
            Settings
          </Link>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>

            {/* Page title - could be dynamic based on current route */}
            <div className="flex-1 lg:ml-0">
              <h2 className="text-lg font-semibold text-gray-900">
                {getPageTitle(pathname)}
              </h2>
            </div>

            {/* Header actions */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {/* Notification badge */}
                <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500"></span>
              </Button>

              {/* User menu */}
              <div className="relative">
                <div className="flex items-center space-x-3">
                  {/* User avatar */}
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white text-sm font-medium">
                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                  </div>

                  {/* User info */}
                  <div className="hidden md:block">
                    <p className="text-sm font-medium text-gray-900">
                      {user?.full_name || 'User'}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">
                      {user?.role || 'user'}
                    </p>
                  </div>

                  {/* Logout button */}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={logout}
                    title="Logout"
                  >
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

/**
 * Get page title based on current pathname.
 * This could be enhanced to be more dynamic or use a routing configuration.
 */
function getPageTitle(pathname: string): string {
  const titleMap: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/clients': 'Clients',
    '/projects': 'Projects',
    '/payments': 'Payments',
    '/expenses': 'Expenses',
    '/invoices': 'Invoices',
    '/users': 'Users',
    '/settings': 'Settings',
  };

  // Check for exact match first
  if (titleMap[pathname]) {
    return titleMap[pathname];
  }

  // Check for partial matches (e.g., /clients/123)
  for (const [path, title] of Object.entries(titleMap)) {
    if (pathname.startsWith(path + '/')) {
      return title;
    }
  }

  return 'Smart CRM';
}
