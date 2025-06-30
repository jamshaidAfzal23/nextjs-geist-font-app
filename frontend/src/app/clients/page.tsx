/**
 * Clients page for Smart CRM SaaS application.
 * Displays a list of clients with search, filtering, and management capabilities.
 * Includes functionality to view, edit, and delete clients.
 */

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth, withAuth } from '@/contexts/auth-context';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner, TableSkeleton } from '@/components/ui/loading';
import { apiClient } from '@/lib/api-client';
import { Client, PaginatedResponse } from '@/types/api';
import { formatDate, getInitials } from '@/lib/utils';
import {
  Search,
  Plus,
  Building2,
  Mail,
  Phone,
  MapPin,
  Edit,
  Trash2,
  Eye,
  Filter,
  Download,
} from 'lucide-react';

/**
 * Clients page component with list view and management capabilities.
 */
function ClientsPage() {
  // State management
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalClients, setTotalClients] = useState(0);

  // Hooks
  const { user } = useAuth();

  // Constants
  const ITEMS_PER_PAGE = 10;

  /**
   * Load clients data on component mount and when search/page changes.
   */
  useEffect(() => {
    loadClients();
  }, [currentPage, searchTerm]);

  /**
   * Load clients from the API with pagination and search.
   */
  const loadClients = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Calculate skip value for pagination
      const skip = (currentPage - 1) * ITEMS_PER_PAGE;

      // Prepare search parameters
      const params = {
        skip,
        limit: ITEMS_PER_PAGE,
        ...(searchTerm && { search: searchTerm }),
      };

      // For demo purposes, we'll simulate the API call with mock data
      // In a real implementation, uncomment the line below:
      // const response = await apiClient.getClients(params);

      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate loading

      const mockClients: Client[] = [
        {
          id: 1,
          company_name: 'Acme Corporation',
          contact_person_name: 'John Smith',
          email: 'john@acme.com',
          phone_number: '+1 (555) 123-4567',
          address: '123 Business St, New York, NY 10001',
          industry: 'Technology',
          platform_preference: 'Web',
          notes: 'Long-term client with multiple projects',
          assigned_user_id: 1,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          total_project_value: 125000,
          active_projects_count: 3,
        },
        {
          id: 2,
          company_name: 'TechStart Inc.',
          contact_person_name: 'Sarah Johnson',
          email: 'sarah@techstart.com',
          phone_number: '+1 (555) 987-6543',
          address: '456 Innovation Ave, San Francisco, CA 94105',
          industry: 'Software',
          platform_preference: 'Mobile',
          notes: 'Startup focused on mobile applications',
          assigned_user_id: 1,
          created_at: '2024-01-20T14:30:00Z',
          updated_at: '2024-01-20T14:30:00Z',
          total_project_value: 75000,
          active_projects_count: 2,
        },
        {
          id: 3,
          company_name: 'Global Solutions Ltd.',
          contact_person_name: 'Michael Brown',
          email: 'michael@globalsolutions.com',
          phone_number: '+1 (555) 456-7890',
          address: '789 Enterprise Blvd, Chicago, IL 60601',
          industry: 'Consulting',
          platform_preference: 'Web',
          notes: 'International consulting firm',
          assigned_user_id: 1,
          created_at: '2024-02-01T09:15:00Z',
          updated_at: '2024-02-01T09:15:00Z',
          total_project_value: 200000,
          active_projects_count: 1,
        },
      ];

      // Filter clients based on search term
      const filteredClients = searchTerm
        ? mockClients.filter(client =>
            client.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            client.contact_person_name.toLowerCase().includes(searchTerm.toLowerCase())
          )
        : mockClients;

      setClients(filteredClients);
      setTotalClients(filteredClients.length);
      setTotalPages(Math.ceil(filteredClients.length / ITEMS_PER_PAGE));
    } catch (err: any) {
      console.error('Failed to load clients:', err);
      setError('Failed to load clients. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle search input change with debouncing.
   */
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Reset to first page when searching
  };

  /**
   * Handle client deletion.
   */
  const handleDeleteClient = async (clientId: number) => {
    if (!confirm('Are you sure you want to delete this client?')) {
      return;
    }

    try {
      // In a real implementation:
      // await apiClient.deleteClient(clientId);
      
      // For demo, just remove from local state
      setClients(prev => prev.filter(client => client.id !== clientId));
      
      // Show success message (you might want to use a toast library)
      alert('Client deleted successfully');
    } catch (err: any) {
      console.error('Failed to delete client:', err);
      alert('Failed to delete client. Please try again.');
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
            <p className="text-gray-600 mt-1">
              Manage your client relationships and contacts
            </p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link href="/clients/new">
                <Plus className="h-4 w-4 mr-2" />
                Add Client
              </Link>
            </Button>
          </div>
        </div>

        {/* Search and filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <Input
                  placeholder="Search clients by name or company..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  leftIcon={<Search className="h-4 w-4" />}
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error state */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <span className="text-red-700">{error}</span>
                <Button variant="outline" size="sm" onClick={loadClients}>
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Clients list */}
        <Card>
          <CardHeader>
            <CardTitle>
              All Clients ({totalClients})
            </CardTitle>
            <CardDescription>
              A list of all clients in your CRM system
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <TableSkeleton rows={5} columns={5} />
            ) : clients.length > 0 ? (
              <div className="space-y-4">
                {/* Table header */}
                <div className="grid grid-cols-12 gap-4 pb-3 border-b text-sm font-medium text-gray-500">
                  <div className="col-span-3">Client</div>
                  <div className="col-span-2">Contact</div>
                  <div className="col-span-2">Industry</div>
                  <div className="col-span-2">Projects</div>
                  <div className="col-span-2">Value</div>
                  <div className="col-span-1">Actions</div>
                </div>

                {/* Table rows */}
                {clients.map((client) => (
                  <div
                    key={client.id}
                    className="grid grid-cols-12 gap-4 py-4 border-b border-gray-100 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    {/* Client info */}
                    <div className="col-span-3 flex items-center space-x-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                        {getInitials(client.company_name)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {client.company_name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {client.contact_person_name}
                        </p>
                      </div>
                    </div>

                    {/* Contact info */}
                    <div className="col-span-2">
                      <div className="flex items-center space-x-1 text-sm text-gray-600">
                        <Mail className="h-3 w-3" />
                        <span className="truncate">{client.email}</span>
                      </div>
                      {client.phone_number && (
                        <div className="flex items-center space-x-1 text-sm text-gray-600 mt-1">
                          <Phone className="h-3 w-3" />
                          <span>{client.phone_number}</span>
                        </div>
                      )}
                    </div>

                    {/* Industry */}
                    <div className="col-span-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {client.industry || 'Not specified'}
                      </span>
                    </div>

                    {/* Projects */}
                    <div className="col-span-2">
                      <p className="text-sm font-medium text-gray-900">
                        {client.active_projects_count || 0} active
                      </p>
                      <p className="text-xs text-gray-500">
                        {client.platform_preference || 'Any platform'}
                      </p>
                    </div>

                    {/* Value */}
                    <div className="col-span-2">
                      <p className="text-sm font-medium text-gray-900">
                        ${(client.total_project_value || 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500">
                        Total value
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="col-span-1 flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        asChild
                        title="View client"
                      >
                        <Link href={`/clients/${client.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        asChild
                        title="Edit client"
                      >
                        <Link href={`/clients/${client.id}/edit`}>
                          <Edit className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteClient(client.id)}
                        title="Delete client"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No clients found
                </h3>
                <p className="text-gray-500 mb-6">
                  {searchTerm
                    ? 'No clients match your search criteria.'
                    : 'Get started by adding your first client.'}
                </p>
                <Button asChild>
                  <Link href="/clients/new">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Client
                  </Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-700">
              Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} to{' '}
              {Math.min(currentPage * ITEMS_PER_PAGE, totalClients)} of{' '}
              {totalClients} clients
            </p>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}

// Export with authentication protection
export default withAuth(ClientsPage);
