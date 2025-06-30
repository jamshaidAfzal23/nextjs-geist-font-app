/**
 * Dashboard page for Smart CRM SaaS application.
 * Provides an overview of key metrics, recent activities, and quick actions.
 * This is the main landing page for authenticated users.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth, withAuth } from '@/contexts/auth-context';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingSpinner, CardSkeleton } from '@/components/ui/loading';
import { apiClient } from '@/lib/api-client';
import { formatCurrency, formatNumber, getStatusColor } from '@/lib/utils';
import {
  Users,
  Building2,
  FolderOpen,
  CreditCard,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  AlertCircle,
  Plus,
} from 'lucide-react';
import Link from 'next/link';
import { AIAssistant } from '@/components/ai-assistant/ai-assistant';

// Dashboard stats interface
interface DashboardStats {
  totalClients: number;
  totalProjects: number;
  totalRevenue: number;
  totalExpenses: number;
  activeProjects: number;
  overdueProjects: number;
  pendingPayments: number;
  monthlyGrowth: number;
}

// Recent activity interface
interface RecentActivity {
  id: string;
  type: 'client' | 'project' | 'payment' | 'expense';
  title: string;
  description: string;
  timestamp: string;
  status?: string;
}

/**
 * Dashboard page component with overview metrics and recent activities.
 */
function DashboardPage() {
  // State management
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hooks
  const { user } = useAuth();

  /**
   * Load dashboard data on component mount.
   */
  useEffect(() => {
    loadDashboardData();
  }, []);

  /**
   * Load dashboard statistics and recent activities.
   */
  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const statsData = await apiClient.getDashboardStats();
      setStats(statsData);

      // Mock activities for now
      const mockActivities: RecentActivity[] = [
        {
          id: '1',
          type: 'client',
          title: 'New client added',
          description: 'Acme Corp has been added to the system',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        },
        {
          id: '2',
          type: 'project',
          title: 'Project completed',
          description: 'Website redesign project has been marked as completed',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          status: 'completed',
        },
        {
          id: '3',
          type: 'payment',
          title: 'Payment received',
          description: '$5,000 payment received from TechStart Inc.',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          status: 'completed',
        },
        {
          id: '4',
          type: 'expense',
          title: 'New expense recorded',
          description: 'Software license expense of $299',
          timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
        },
      ];
      setRecentActivities(mockActivities);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get icon for activity type.
   */
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'client':
        return <Building2 className="h-4 w-4" />;
      case 'project':
        return <FolderOpen className="h-4 w-4" />;
      case 'payment':
        return <CreditCard className="h-4 w-4" />;
      case 'expense':
        return <DollarSign className="h-4 w-4" />;
      default:
        return <Calendar className="h-4 w-4" />;
    }
  };

  /**
   * Format relative time for activities.
   */
  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Welcome section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
            </h1>
            <p className="text-gray-600 mt-1">
              Here's what's happening with your business today.
            </p>
          </div>
          <div className="flex space-x-3">
            <Link href="/clients/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Client
              </Button>
            </Link>
            <Link href="/projects/new">
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </Link>
          </div>
        </div>

        {/* Error state */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadDashboardData}
                  className="ml-auto"
                >
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {isLoading ? (
            // Loading skeletons
            Array.from({ length: 4 }).map((_, index) => (
              <CardSkeleton key={index} />
            ))
          ) : stats ? (
            <>
              {/* Total Revenue */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      +{stats.monthlyGrowth}% from last month
                    </span>
                  </p>
                </CardContent>
              </Card>

              {/* Total Clients */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(stats.totalClients)}</div>
                  <p className="text-xs text-muted-foreground">
                    Active client relationships
                  </p>
                </CardContent>
              </Card>

              {/* Active Projects */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
                  <FolderOpen className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.activeProjects}</div>
                  <p className="text-xs text-muted-foreground">
                    {stats.overdueProjects} overdue projects
                  </p>
                </CardContent>
              </Card>

              {/* Pending Payments */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Pending Payments</CardTitle>
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(stats.pendingPayments)}</div>
                  <p className="text-xs text-muted-foreground">
                    Awaiting payment
                  </p>
                </CardContent>
              </Card>
            </>
          ) : null}
        </div>

        {/* Recent activities and quick actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activities */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>
                  Latest updates from your CRM system
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                          <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : recentActivities.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivities.map((activity) => (
                      <div key={activity.id} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">
                            {activity.title}
                          </p>
                          <p className="text-sm text-gray-500">
                            {activity.description}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatRelativeTime(activity.timestamp)}
                          </p>
                        </div>
                        {activity.status && (
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                            {activity.status}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No recent activities
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link href="/clients/new" className="block">
                  <Button className="w-full justify-start">
                    <Building2 className="h-4 w-4 mr-2" />
                    Add New Client
                  </Button>
                </Link>
                <Link href="/projects/new" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <FolderOpen className="h-4 w-4 mr-2" />
                    Create Project
                  </Button>
                </Link>
                <Link href="/payments/new" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Record Payment
                  </Button>
                </Link>
                <Link href="/expenses/new" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <DollarSign className="h-4 w-4 mr-2" />
                    Add Expense
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <div className="mt-12">
        <AIAssistant />
      </div>
    </MainLayout>
  );
}

// Export with authentication protection
export default withAuth(DashboardPage);
