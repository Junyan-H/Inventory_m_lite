import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getActiveCheckouts } from '@/api';
import { Card, Badge, Loading, Button } from '@/components/ui';
import { CheckinModal } from '@/components/features/CheckinModal';
import { format } from 'date-fns';
import type { ActiveCheckout } from '@/types';

export const CheckoutsPage: React.FC = () => {
  const [isCheckinModalOpen, setIsCheckinModalOpen] = useState(false);
  const [selectedCheckout, setSelectedCheckout] = useState<ActiveCheckout | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['active-checkouts'],
    queryFn: () => getActiveCheckouts(),
  });

  const handleCheckinClick = (checkout: ActiveCheckout) => {
    setSelectedCheckout(checkout);
    setIsCheckinModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsCheckinModalOpen(false);
    setSelectedCheckout(null);
  };

  if (isLoading) {
    return <Loading text="Loading active checkouts..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading checkouts: {(error as Error).message}</p>
      </div>
    );
  }

  const checkouts = data?.checkouts || [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Active Checkouts</h1>
        <p className="text-gray-600">
          {checkouts.length} active checkout{checkouts.length !== 1 ? 's' : ''}
        </p>
      </div>

      {checkouts.length === 0 ? (
        <Card>
          <p className="text-center text-gray-600">No active checkouts</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {checkouts.map((checkout) => (
            <Card key={checkout.checkout_id}>
              <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                <div className="flex-1 mb-4 md:mb-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <Link
                        to={`/item/${checkout.item_id}`}
                        className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                      >
                        {checkout.item_name}
                      </Link>
                      <p className="text-sm text-gray-600 capitalize">
                        {checkout.category} • {checkout.location.replace('_', ' ')}
                      </p>
                    </div>
                    {checkout.is_overdue && (
                      <Badge variant="danger">{checkout.days_overdue} days overdue</Badge>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p className="text-sm text-gray-600">Checked out by</p>
                      <p className="font-medium">{checkout.full_name}</p>
                      <p className="text-sm text-gray-500">{checkout.ldap} • {checkout.email}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Checkout Date</p>
                      <p className="font-medium">
                        {format(new Date(checkout.checkout_date), 'MM/dd/yyyy h:mm a')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Expected Return</p>
                      <p className="font-medium">
                        {checkout.expected_return_datetime
                          ? format(new Date(checkout.expected_return_datetime), 'MM/dd/yyyy h:mm a')
                          : 'Not specified'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Quantity</p>
                      <p className="font-medium">{checkout.quantity}</p>
                    </div>
                  </div>

                  {checkout.notes && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm text-gray-600">Notes</p>
                      <p className="text-sm text-gray-800">{checkout.notes}</p>
                    </div>
                  )}
                </div>

                <div className="md:ml-6">
                  <Button
                    variant="primary"
                    className="w-full md:w-auto whitespace-nowrap"
                    onClick={() => handleCheckinClick(checkout)}
                  >
                    Check In
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Check-in Modal */}
      {selectedCheckout && (
        <CheckinModal
          isOpen={isCheckinModalOpen}
          onClose={handleCloseModal}
          checkout={selectedCheckout}
        />
      )}
    </div>
  );
};