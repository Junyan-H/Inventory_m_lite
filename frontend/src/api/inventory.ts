import apiClient from './client';
import type {
  InventoryResponse,
  SearchResponse,
  ItemDetailsResponse,
} from '@/types';

/**
 * Get inventory items for a specific location
 */
export const getInventory = async (location: string, ldap?: string): Promise<InventoryResponse> => {
  const params = new URLSearchParams({ location });
  if (ldap) params.append('ldap', ldap);

  const response = await apiClient.get<InventoryResponse>(`/api/inventory?${params}`);
  return response.data;
};

/**
 * Search inventory items by name or category
 */
export const searchInventory = async (query: string, location?: string): Promise<SearchResponse> => {
  const params = new URLSearchParams({ q: query });
  if (location) params.append('location', location);

  const response = await apiClient.get<SearchResponse>(`/api/inventory/search?${params}`);
  return response.data;
};

/**
 * Get detailed information for a specific item
 */
export const getItemDetails = async (itemId: number): Promise<ItemDetailsResponse> => {
  const response = await apiClient.get<ItemDetailsResponse>(`/api/inventory/${itemId}`);
  return response.data;
};