import apiClient from './client';
import type {
  CheckoutFormData,
  CheckinFormData,
  CheckoutResponse,
  CheckinResponse,
  ActiveCheckoutsResponse,
  CheckoutHistoryResponse,
} from '@/types';

/**
 * Check out an item to a user
 */
export const checkoutItem = async (data: CheckoutFormData): Promise<CheckoutResponse> => {
  const response = await apiClient.post<CheckoutResponse>('/api/checkout', data);
  return response.data;
};

/**
 * Check in an item (return it)
 */
export const checkinItem = async (data: CheckinFormData): Promise<CheckinResponse> => {
  const response = await apiClient.post<CheckinResponse>('/api/checkout/checkin', data);
  return response.data;
};

/**
 * Get all active checkouts
 */
export const getActiveCheckouts = async (data: CheckinFormData): Promise<ActiveCheckoutsResponse> => {
  const response = await apiClient.get<ActiveCheckoutsResponse>('api/checkout/active', data);
  return response.data;
};

/**
 * Get all overdue checkouts
 */
export const getOverdueCheckouts = async (): Promise<ActiveCheckoutsResponse> => {
  const response = await apiClient.get<ActiveCheckoutsResponse>('/api/checkout/overdue');
  return response.data;
};

/**
 * Get checkout history for a specific user (by LDAP)
 */
export const getUserCheckoutHistory = async (
  ldap: string,
  limit: number = 50
): Promise<CheckoutHistoryResponse> => {
  const response = await apiClient.get<CheckoutHistoryResponse>(
    `/api/checkout/user/${ldap}?limit=${limit}`
  );
  return response.data;
};

/**
 * Get checkout history for a specific item
 */
export const getItemCheckoutHistory = async (
  itemId: number,
  limit: number = 50
): Promise<CheckoutHistoryResponse> => {
  const response = await apiClient.get<CheckoutHistoryResponse>(
    `/api/checkout/item/${itemId}/history?limit=${limit}`
  );
  return response.data;
};