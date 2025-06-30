/**
 * TypeScript type definitions for Smart CRM SaaS API.
 * This file contains all the type definitions that match the backend Pydantic schemas.
 */

// Base types
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

// User types
export interface User extends BaseEntity {
  full_name: string;
  email: string;
  role: 'admin' | 'manager' | 'developer' | 'user' | 'viewer';
  is_active: boolean;
  is_verified: boolean;
}

export interface UserCreate {
  full_name: string;
  email: string;
  role: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserToken {
  access_token: string;
  token_type: string;
  user: User;
}

// Client types
export interface Client extends BaseEntity {
  company_name: string;
  contact_person_name: string;
  email: string;
  phone_number?: string;
  address?: string;
  industry?: string;
  platform_preference?: string;
  notes?: string;
  assigned_user_id: number;
  total_project_value?: number;
  active_projects_count?: number;
}

export interface ClientCreate {
  company_name: string;
  contact_person_name: string;
  email: string;
  phone_number?: string;
  address?: string;
  industry?: string;
  platform_preference?: string;
  notes?: string;
  assigned_user_id: number;
}

// Project types
export type ProjectStatus = 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled';
export type ProjectPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Project extends BaseEntity {
  title: string;
  description?: string;
  status: ProjectStatus;
  priority: ProjectPriority;
  start_date?: string;
  end_date?: string;
  actual_end_date?: string;
  budget: number;
  hourly_rate?: number;
  client_id: number;
  developer_id?: number;
  is_overdue?: boolean;
  total_expenses?: number;
  total_payments?: number;
  profit_margin?: number;
  client_name?: string;
  developer_name?: string;
}

export interface ProjectCreate {
  title: string;
  description?: string;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  start_date?: string;
  end_date?: string;
  budget: number;
  hourly_rate?: number;
  client_id: number;
  developer_id?: number;
}

// Financial types
export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';
export type PaymentMethod = 'bank_transfer' | 'credit_card' | 'paypal' | 'cryptocurrency';
export type ExpenseCategory = 'software' | 'hardware' | 'services' | 'marketing' | 'travel' | 'other';
export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';

export interface Payment extends BaseEntity {
  amount: number;
  status: PaymentStatus;
  method: PaymentMethod;
  transaction_id?: string;
  project_id: number;
  client_id: number;
  payment_date?: string;
  notes?: string;
  project_title?: string;
  client_name?: string;
}

export interface PaymentCreate {
  amount: number;
  status?: PaymentStatus;
  method: PaymentMethod;
  transaction_id?: string;
  project_id: number;
  client_id: number;
  payment_date?: string;
  notes?: string;
}

export interface Expense extends BaseEntity {
  title: string;
  amount: number;
  category: ExpenseCategory;
  linked_project_id?: number;
  created_by_id: number;
  receipt_url?: string;
  notes?: string;
  expense_date?: string;
  project_title?: string;
  created_by_name?: string;
}

export interface ExpenseCreate {
  title: string;
  amount: number;
  category: ExpenseCategory;
  linked_project_id?: number;
  created_by_id: number;
  receipt_url?: string;
  notes?: string;
  expense_date?: string;
}

export interface Invoice extends BaseEntity {
  invoice_number: string;
  client_id: number;
  amount: number;
  status: InvoiceStatus;
  issue_date: string;
  due_date: string;
  paid_date?: string;
  items: any[];
  notes?: string;
  client_name?: string;
  is_overdue?: boolean;
  days_until_due?: number;
}

export interface InvoiceCreate {
  invoice_number: string;
  client_id: number;
  amount: number;
  status?: InvoiceStatus;
  issue_date: string;
  due_date: string;
  items: any[];
  notes?: string;
}

// Statistics and analytics types
export interface FinancialStats {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  profit_margin: number;
  revenue_by_month: Record<string, number>;
  expenses_by_category: Record<string, number>;
  outstanding_invoices: number;
  average_payment_time?: number;
}

export interface ProjectStats {
  total_projects: number;
  projects_by_status: Record<string, number>;
  projects_by_priority: Record<string, number>;
  overdue_projects: number;
  total_budget: number;
  average_project_duration?: number;
  completion_rate: number;
}

export interface ClientStats {
  total_clients: number;
  active_clients: number;
  clients_by_industry: Record<string, number>;
  clients_by_user: Record<string, number>;
  average_project_value: number;
  top_clients_by_value: Array<{
    id: number;
    name: string;
    total_value: number;
  }>;
}

// API Response types
export interface PaginatedResponse<T> {
  items?: T[];
  users?: T[];
  clients?: T[];
  projects?: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface ApiError {
  error: string;
  message?: string;
  status_code?: number;
}

// API endpoints configuration
export interface ApiEndpoints {
  users: string;
  clients: string;
  projects: string;
  payments: string;
  expenses: string;
  invoices: string;
  financial: string;
}

// Search and filter types
export interface SearchFilters {
  search_term?: string;
  page?: number;
  per_page?: number;
  [key: string]: any;
}

export interface ClientFilters extends SearchFilters {
  industry?: string;
  assigned_user_id?: number;
  platform_preference?: string;
  has_active_projects?: boolean;
  created_after?: string;
  created_before?: string;
}

export interface ProjectFilters extends SearchFilters {
  status?: ProjectStatus;
  priority?: ProjectPriority;
  client_id?: number;
  developer_id?: number;
  is_overdue?: boolean;
  budget_min?: number;
  budget_max?: number;
  start_date_after?: string;
  end_date_before?: string;
}
