import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getItemDetails, getItemCheckoutHistory } from '@/api';
import { Card, Badge, Loading, Button } from '@/components/ui';
import { CheckoutModal } from '@/components/features/CheckoutModal';
import { format } from 'date-fns';

export const ItemDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const itemId = parseInt(id || '0');
  const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);

  const { data: itemData, isLoading: itemLoading } = useQuery({
    queryKey: ['item', itemId],
    queryFn: () => getItemDetails(itemId),
    enabled: !!itemId,
  });

  const { data: historyData } = useQuery({
    queryKey: ['item-history', itemId],
    queryFn: () => getItemCheckoutHistory(itemId, 20),
    enabled: !!itemId,
  });

  if (itemLoading) {
    return <Loading text="Loading item details..." />;
  }

  if (!itemData?.item) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Item not found</p>
        <Link to="/inventory" className="btn-primary mt-4 inline-block">
          Back to Inventory
        </Link>
      </div>
    );
  }

  const item = itemData.item;

  const getAvailabilityBadge = () => {
    if (item.quantity_available === 0) {
      return <Badge variant="danger">Out of Stock</Badge>;
    } else if (item.quantity_available < item.quantity_total * 0.2) {
      return <Badge variant="warning">Low Stock</Badge>;
    } else {
      return <Badge variant="success">Available</Badge>;
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Link to="/inventory" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
          ← Back to Inventory
        </Link>
        <div className="flex justify-between items-start">
          <h1 className="text-3xl font-bold text-gray-900">{item.item_name}</h1>
          {getAvailabilityBadge()}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <h2 className="text-xl font-semibold mb-4">Item Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Category</p>
                <p className="font-medium capitalize">{item.category}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Location</p>
                <p className="font-medium capitalize">{item.location.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Quantity</p>
                <p className="font-medium">{item.quantity_total}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Available</p>
                <p className="font-medium">{item.quantity_available}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Checked Out</p>
                <p className="font-medium">{item.quantity_checked_out}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Condition</p>
                <p className="font-medium capitalize">{item.condition}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-medium capitalize">{item.status}</p>
              </div>
              {item.purchase_price && (
                <div>
                  <p className="text-sm text-gray-600">Purchase Price</p>
                  <p className="font-medium">${item.purchase_price.toFixed(2)}</p>
                </div>
              )}
              {item.restock_date && (
                <div>
                  <p className="text-sm text-gray-600">Restock Date</p>
                  <p className="font-medium">{format(new Date(item.restock_date), 'MM/dd/yyyy')}</p>
                </div>
              )}
              {item.last_audit_date && (
                <div>
                  <p className="text-sm text-gray-600">Last Audit</p>
                  <p className="font-medium">{format(new Date(item.last_audit_date), 'MM/dd/yyyy')}</p>
                </div>
              )}
            </div>
            {item.notes && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600 mb-1">Notes</p>
                <p className="text-gray-800">{item.notes}</p>
              </div>
            )}
          </Card>

          {historyData && historyData.history.length > 0 && (
            <Card className="mt-6">
              <h2 className="text-xl font-semibold mb-4">Checkout History</h2>
              <div className="space-y-3">
                {historyData.history.map((record) => (
                  <div key={record.history_id} className="border-b pb-3 last:border-b-0">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{record.full_name} ({record.ldap})</p>
                        <p className="text-sm text-gray-600">
                          Checked out: {format(new Date(record.checkout_date), 'MM/dd/yyyy h:mm a')}
                        </p>
                        {record.return_date && (
                          <p className="text-sm text-gray-600">
                            Returned: {format(new Date(record.return_date), 'MM/dd/yyyy h:mm a')}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm">Qty: {record.quantity}</p>
                        {record.late_return && (
                          <Badge variant="danger" className="mt-1">Late</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        <div>
          <Card>
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              {item.quantity_available > 0 ? (
                <Button
                  variant="primary"
                  className="w-full"
                  onClick={() => setIsCheckoutModalOpen(true)}
                >
                  Checkout Item
                </Button>
              ) : (
                <Button variant="secondary" className="w-full" disabled>
                  Out of Stock
                </Button>
              )}
              <Link to={`/checkouts?item_id=${item.item_id}`} className="block">
                <Button variant="secondary" className="w-full">
                  View Active Checkouts
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>

      {/* Checkout Modal */}
      <CheckoutModal
        isOpen={isCheckoutModalOpen}
        onClose={() => setIsCheckoutModalOpen(false)}
        item={item}
      />
    </div>
  );
};