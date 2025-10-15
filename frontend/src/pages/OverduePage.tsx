import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getOverdueCheckouts } from '@/api';
import { Card, Badge, Loading, Button } from '@/components/ui';
import { CheckinModal } from '@/components/features/CheckinModal';
import { format } from 'date-fns';
import type { ActiveCheckout } from '@/types';

export const OverduePage: React.FC = () => {
  const [isCheckinModalOpen, setIsCheckinModalOpen] = useState(false);
  const [selectedCheckout, setSelectedCheckout] = useState<ActiveCheckout | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['overdue-checkouts'],
    queryFn: () => getOverdueCheckouts(),
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
    return <Loading text="Loading overdue checkouts..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading overdue checkouts: {(error as Error).message}</p>
      </div>
    );
  }

  const checkouts = data?.checkouts || [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-red-600 mb-2">Overdue Checkouts</h1>
        <p className="text-gray-600">
          {checkouts.length} overdue item{checkouts.length !== 1 ? 's' : ''}
        </p>
      </div>

      {checkouts.length === 0 ? (
        <Card>
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="mt-2 text-gray-600 font-medium">No overdue checkouts!</p>
            <p className="text-sm text-gray-500">All items are returned on time</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {checkouts.map((checkout) => (
            <Card key={checkout.checkout_id} className="border-l-4 border-l-red-500">
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
                        {checkout.location.replace('_', ' ')}
                      </p>
                    </div>
                    <Badge variant="danger" className="text-base">
                      {checkout.days_overdue} days overdue
                    </Badge>
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
                      <p className="font-medium text-red-600">
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
                </div>

                <div className="md:ml-6 flex flex-col space-y-2">
                  <Button
                    variant="primary"
                    className="whitespace-nowrap"
                    onClick={() => handleCheckinClick(checkout)}
                  >
                    Check In Now
                  </Button>
                  <a
                    href={`mailto:${checkout.email}?subject=Overdue Item: ${checkout.item_name}`}
                    className="btn-secondary text-center whitespace-nowrap"
                  >
                    Send Reminder
                  </a>
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