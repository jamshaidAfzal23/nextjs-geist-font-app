/**
 * API Client for Smart CRM SaaS application.
 * This module provides a centralized way to communicate with the backend API.
 * It includes authentication, error handling, and type-safe API calls.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  User, UserCreate, UserLogin, UserToken,
  Client, ClientCreate,
  Project, ProjectCreate,
  Payment, PaymentCreate,
  Expense, ExpenseCreate,
  Invoice, InvoiceCreate,
  FinancialStats, ProjectStats, ClientStats,
  PaginatedResponse, ApiError
} from '@/types/api';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * API Client class that handles all HTTP requests to the backend.
 * Provides authentication, error handling, and type-safe methods.
 */
class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    // Create axios instance with base configuration
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add authentication token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          this.clearToken();
          // Redirect to login page
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(this.handleError(error));
      }
    );

    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('access_token');
      if (savedToken) {
        this.token = savedToken;
      }
    }
  }

  /**
   * Handle API errors and format them consistently.
   */
  private handleError(error: AxiosError): ApiError {
    if (error.response?.data) {
      return error.response.data as ApiError;
    }
    
    return {
      error: error.message || 'An unexpected error occurred',
      status_code: error.response?.status || 500,
    };
  }

  /**
   * Set authentication token for API requests.
   */
  setToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  /**
   * Clear authentication token.
   */
  clearToken(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return !!this.token;
  }

  // ==================== AUTH ENDPOINTS ====================

  /**
   * Login user and set authentication token.
   */
  async login(credentials: UserLogin): Promise<UserToken> {
    const response = await this.client.post<UserToken>('/api/v1/users/login', credentials);
    this.setToken(response.data.access_token);
    return response.data;
  }

  /**
   * Logout user and clear authentication token.
   */
  logout(): void {
    this.clearToken();
  }

  // ==================== USER ENDPOINTS ====================

  /**
   * Create a new user.
   */
  async createUser(userData: UserCreate): Promise<User> {
    const response = await this.client.post<User>('/users/', userData);
    return response.data;
  }

  /**
   * Get paginated list of users.
   */
  async getUsers(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    role?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<User>> {
    const response = await this.client.get<PaginatedResponse<User>>('/users/', { params });
    return response.data;
  }

  /**
   * Get user by ID.
   */
  async getUser(userId: number): Promise<User> {
    const response = await this.client.get<User>(`/users/${userId}`);
    return response.data;
  }

  /**
   * Update user information.
   */
  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response = await this.client.put<User>(`/users/${userId}`, userData);
    return response.data;
  }

  /**
   * Delete user.
   */
  async deleteUser(userId: number): Promise<void> {
    await this.client.delete(`/users/${userId}`);
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/users/me');
    return response.data;
  }

  // ==================== CLIENT ENDPOINTS ====================

  /**
   * Create a new client.
   */
  async createClient(clientData: ClientCreate): Promise<Client> {
    const response = await this.client.post<Client>('/clients/', clientData);
    return response.data;
  }

  /**
   * Get paginated list of clients.
   */
  async getClients(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    industry?: string;
    platform?: string;
    assigned_user_id?: number;
  }): Promise<PaginatedResponse<Client>> {
    const response = await this.client.get<PaginatedResponse<Client>>('/clients/', { params });
    return response.data;
  }

  /**
   * Get client by ID.
   */
  async getClient(clientId: number): Promise<Client> {
    const response = await this.client.get<Client>(`/clients/${clientId}`);
    return response.data;
  }

  /**
   * Update client information.
   */
  async updateClient(clientId: number, clientData: Partial<Client>): Promise<Client> {
    const response = await this.client.put<Client>(`/clients/${clientId}`, clientData);
    return response.data;
  }

  /**
   * Delete client.
   */
  async deleteClient(clientId: number): Promise<void> {
    await this.client.delete(`/clients/${clientId}`);
  }

  /**
   * Get client statistics.
   */
  async getClientStats(): Promise<ClientStats> {
    const response = await this.client.get<ClientStats>('/clients/summary/stats');
    return response.data;
  }

  // ==================== PROJECT ENDPOINTS ====================

  /**
   * Create a new project.
   */
  async createProject(projectData: ProjectCreate): Promise<Project> {
    const response = await this.client.post<Project>('/projects/', projectData);
    return response.data;
  }

  /**
   * Get paginated list of projects.
   */
  async getProjects(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
    priority?: string;
    client_id?: number;
    developer_id?: number;
    is_overdue?: boolean;
  }): Promise<PaginatedResponse<Project>> {
    const response = await this.client.get<PaginatedResponse<Project>>('/projects/', { params });
    return response.data;
  }

  /**
   * Get project by ID.
   */
  async getProject(projectId: number): Promise<Project> {
    const response = await this.client.get<Project>(`/projects/${projectId}`);
    return response.data;
  }

  /**
   * Update project information.
   */
  async updateProject(projectId: number, projectData: Partial<Project>): Promise<Project> {
    const response = await this.client.put<Project>(`/projects/${projectId}`, projectData);
    return response.data;
  }

  /**
   * Delete project.
   */
  async deleteProject(projectId: number): Promise<void> {
    await this.client.delete(`/projects/${projectId}`);
  }

  /**
   * Mark project as completed.
   */
  async completeProject(projectId: number): Promise<Project> {
    const response = await this.client.post<Project>(`/projects/${projectId}/complete`);
    return response.data;
  }

  /**
   * Get project statistics.
   */
  async getProjectStats(): Promise<ProjectStats> {
    const response = await this.client.get<ProjectStats>('/projects/summary/stats');
    return response.data;
  }

  // ==================== FINANCIAL ENDPOINTS ====================

  /**
   * Create a new payment.
   */
  async createPayment(paymentData: PaymentCreate): Promise<Payment> {
    const response = await this.client.post<Payment>('/payments/', paymentData);
    return response.data;
  }

  /**
   * Get list of payments.
   */
  async getPayments(params?: {
    skip?: number;
    limit?: number;
    project_id?: number;
    client_id?: number;
    status?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<Payment[]> {
    const response = await this.client.get<Payment[]>('/payments/', { params });
    return response.data;
  }

  /**
   * Create a new expense.
   */
  async createExpense(expenseData: ExpenseCreate): Promise<Expense> {
    const response = await this.client.post<Expense>('/expenses/', expenseData);
    return response.data;
  }

  /**
   * Get list of expenses.
   */
  async getExpenses(params?: {
    skip?: number;
    limit?: number;
    project_id?: number;
    category?: string;
    created_by_id?: number;
    date_from?: string;
    date_to?: string;
  }): Promise<Expense[]> {
    const response = await this.client.get<Expense[]>('/expenses/', { params });
    return response.data;
  }

  /**
   * Create a new invoice.
   */
  async createInvoice(invoiceData: InvoiceCreate): Promise<Invoice> {
    const response = await this.client.post<Invoice>('/invoices/', invoiceData);
    return response.data;
  }

  /**
   * Get list of invoices.
   */
  async getInvoices(params?: {
    skip?: number;
    limit?: number;
    client_id?: number;
    status?: string;
    overdue_only?: boolean;
  }): Promise<Invoice[]> {
    const response = await this.client.get<Invoice[]>('/invoices/', { params });
    return response.data;
  }

  /**
   * Get financial statistics.
   */
  async getFinancialStats(year?: number): Promise<FinancialStats> {
    const response = await this.client.get<FinancialStats>('/financial/stats', {
      params: year ? { year } : undefined,
    });
    return response.data;
  }

  // ==================== DASHBOARD ENDPOINTS ====================

  async getDashboardStats(): Promise<any> {
    const response = await this.client.get<any>('/api/v1/dashboard/stats');
    return response.data;
  }

  // ==================== AI ASSISTANT ENDPOINTS ====================

  async getAIAssistantResponse(actionType: string, inputText?: string, relatedId?: number): Promise<any> {
    const response = await this.client.post<any>('/api/v1/ai-assistant', {
      action_type: actionType,
      input_text: inputText,
      related_id: relatedId,
    });
    return response.data;
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Test API connection.
   */
  async testConnection(): Promise<{ status: string; message: string }> {
    const response = await this.client.get('/');
    return response.data;
  }

  /**
   * Get API health status.
   */
  async getHealthStatus(): Promise<{ status: string; timestamp: number }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export the class for testing purposes
export { ApiClient };
