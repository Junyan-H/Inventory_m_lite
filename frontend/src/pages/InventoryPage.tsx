import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getInventory, searchInventory } from '@/api';
import { useApp } from '@/context/AppContext';
import { ItemCard } from '@/components/features/ItemCard';
import { Loading } from '@/components/ui';
import type { Item } from '@/types';

export const InventoryPage: React.FC = () => {
  const { currentLocation } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['inventory', currentLocation, debouncedSearch],
    queryFn: async () => {
      if (debouncedSearch) {
        return await searchInventory(debouncedSearch, currentLocation);
      }
      return await getInventory(currentLocation);
    },
  });

  const items = (data && 'items' in data) ? data.items : [];

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading inventory: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Inventory</h1>
        <p className="text-gray-600 capitalize">Location: {currentLocation.replace('_', ' ')}</p>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search items by name or category..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {isLoading ? (
        <Loading />
      ) : items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">No items found</p>
        </div>
      ) : (
        <div>
          <div className="mb-4 text-sm text-gray-600">
            Showing {items.length} item{items.length !== 1 ? 's' : ''}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item: Item) => (
              <ItemCard key={item.item_id} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};