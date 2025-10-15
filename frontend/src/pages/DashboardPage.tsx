import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getInventory, getActiveCheckouts, getOverdueCheckouts } from '@/api';
import { useApp } from '@/context/AppContext';
import { Card, Badge, Loading } from '@/components/ui';

export const DashboardPage: React.FC = () => {
  const { currentLocation } = useApp();

  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory', currentLocation],
    queryFn: () => getInventory(currentLocation),
  });

  const { data: checkoutsData, isLoading: checkoutsLoading } = useQuery({
    queryKey: ['active-checkouts'],
    queryFn: () => getActiveCheckouts(),
  });

  const { data: overdueData, isLoading: overdueLoading } = useQuery({
    queryKey: ['overdue-checkouts'],
    queryFn: () => getOverdueCheckouts(),
  });

  const isLoading = inventoryLoading || checkoutsLoading || overdueLoading;

  if (isLoading) {
    return <Loading text="Loading dashboard..." />;
  }

  const items = inventoryData?.items || [];
  const activeCheckouts = checkoutsData?.checkouts || [];
  const overdueCheckouts = overdueData?.checkouts || [];

  const stats = {
    totalItems: items.length,
    availableItems: items.filter(item => item.quantity_available > 0).length,
    outOfStock: items.filter(item => item.quantity_available === 0).length,
    lowStock: items.filter(item =>
      item.quantity_available > 0 &&
      item.quantity_available < item.quantity_total * 0.2
    ).length,
    activeCheckouts: activeCheckouts.length,
    overdueCheckouts: overdueCheckouts.length,
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600 capitalize">
          Overview for {currentLocation.replace('_', ' ')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Link to="/inventory">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Items</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalItems}</p>
              </div>
              <div className="text-primary-600">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-600">
              {stats.availableItems} available
            </div>
          </Card>
        </Link>

        <Link to="/checkouts">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-600 mb-1">Active Checkouts</p>
                <p className="text-3xl font-bold text-gray-900">{stats.activeCheckouts}</p>
              </div>
              <div className="text-blue-600">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </Card>
        </Link>

        <Link to="/overdue">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-600 mb-1">Overdue Items</p>
                <p className="text-3xl font-bold text-red-600">{stats.overdueCheckouts}</p>
              </div>
              <div className="text-red-600">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </Card>
        </Link>

        <Card>
          <p className="text-sm text-gray-600 mb-1">Out of Stock</p>
          <p className="text-3xl font-bold text-gray-900">{stats.outOfStock}</p>
          <Badge variant="danger" className="mt-2">Needs Restock</Badge>
        </Card>

        <Card>
          <p className="text-sm text-gray-600 mb-1">Low Stock</p>
          <p className="text-3xl font-bold text-gray-900">{stats.lowStock}</p>
          <Badge variant="warning" className="mt-2">Monitor</Badge>
        </Card>

        <Card className="flex items-center justify-center">
          <Link to="/inventory" className="btn-primary w-full text-center">
            View All Inventory
          </Link>
        </Card>
      </div>

      {overdueCheckouts.length > 0 && (
        <Card>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Recent Overdue Items</h2>
            <Link to="/overdue" className="text-primary-600 hover:text-primary-700 text-sm">
              View All →
            </Link>
          </div>
          <div className="space-y-3">
            {overdueCheckouts.slice(0, 5).map((checkout) => (
              <div key={checkout.checkout_id} className="flex justify-between items-center border-b pb-3 last:border-b-0">
                <div>
                  <p className="font-medium">{checkout.item_name}</p>
                  <p className="text-sm text-gray-600">{checkout.full_name} ({checkout.ldap})</p>
                </div>
                <Badge variant="danger">{checkout.days_overdue} days overdue</Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};