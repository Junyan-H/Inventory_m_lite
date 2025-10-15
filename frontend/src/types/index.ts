// User types
export interface User {
  user_id: number;
  ldap: string;
  full_name: string;
  email: string | null;
  role: string;
  department: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

// Item types
export interface Item {
  item_id: number;
  item_name: string;
  category: string;
  location: string;
  quantity_total: number;
  quantity_available: number;
  quantity_checked_out: number;
  purchase_price: number | null;
  restock_date: string | null;
  condition: string;
  status: string;
  last_audit_date: string | null;
  notes: string | null;
  image_url: string | null;
  created_at?: string;
  updated_at?: string;
  availability_status?: 'Available' | 'Low Stock' | 'Out of Stock';
}

// Checkout types
export interface Checkout {
  checkout_id: number;
  item_id: number;
  user_id: number;
  quantity: number;
  checkout_date: string;
  expected_return_datetime: string;
  checkout_condition: string;
  notes: string | null;
  created_at: string;
}

// Active Checkout with user and item details
export interface ActiveCheckout {
  checkout_id: number;
  checkout_date: string;
  expected_return_datetime: string | null;
  quantity: number;
  ldap: string;
  full_name: string;
  email: string;
  item_id: number;
  item_name: string;
  category: string;
  location: string;
  is_overdue: boolean;
  days_overdue: number;
  notes: string | null;
}

// Checkout History types
export interface CheckoutHistory {
  history_id: number;
  item_id: number;
  user_id: number;
  quantity: number;
  checkout_date: string;
  return_date: string | null;
  expected_return_datetime: string | null;
  checkout_condition: string;
  return_condition: string | null;
  is_returned: boolean;
  late_return: boolean;
  checkout_notes: string | null;
  return_notes: string | null;
  created_at: string;
  updated_at: string;
  // Additional fields from view
  ldap?: string;
  full_name?: string;
  item_name?: string;
  category?: string;
  location?: string;
}

// API Response types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface InventoryResponse {
  success: boolean;
  location: string;
  user: {
    ldap: string;
    full_name: string;
  } | null;
  total_items: number;
  items: Item[];
}

export interface SearchResponse {
  success: boolean;
  query: string;
  location: string | null;
  total_results: number;
  items: Item[];
}

export interface ItemDetailsResponse {
  success: boolean;
  item: Item;
}

export interface CheckoutResponse {
  success: boolean;
  message: string;
  checkout: Checkout;
}

export interface CheckinResponse {
  success: boolean;
  message: string;
  history: CheckoutHistory;
}

export interface ActiveCheckoutsResponse {
  success: boolean;
  total_active_checkouts: number;
  checkouts: ActiveCheckout[];
}

export interface CheckoutHistoryResponse {
  success: boolean;
  total_records: number;
  history: CheckoutHistory[];
  user?: {
    ldap: string;
    full_name: string;
  };
  item_id?: number;
}

// Form types
export interface CheckoutFormData {
  item_id: number;
  user_ldap: string;
  quantity: number;
  expected_return_datetime?: string;
  checkout_condition: string;
  notes?: string;
}

export interface CheckinFormData {
  checkout_id: number;
  return_condition: string;
  return_notes?: string;
}

// Filter and Sort types
export type SortField = 'item_name' | 'category' | 'quantity_available' | 'location';
export type SortDirection = 'asc' | 'desc';

export interface ItemFilters {
  search: string;
  category: string;
  status: string;
  minAvailable: number;
}