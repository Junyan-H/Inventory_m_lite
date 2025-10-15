import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal, Button } from '@/components/ui';
import { checkinItem } from '@/api';
import type { ActiveCheckout } from '@/types';
import { format } from 'date-fns';

interface CheckinModalProps {
  isOpen: boolean;
  onClose: () => void;
  checkout: ActiveCheckout;
}

export const CheckinModal: React.FC<CheckinModalProps> = ({
  isOpen,
  onClose,
  checkout,
}) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    returnCondition: 'good' as const,
    returnNotes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const checkinMutation = useMutation({
    mutationFn: checkinItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['item', checkout.item_id] });
      queryClient.invalidateQueries({ queryKey: ['item-history', checkout.item_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['active-checkouts'] });
      queryClient.invalidateQueries({ queryKey: ['overdue-checkouts'] });
      onClose();
      resetForm();
    },
    onError: (error: any) => {
      setErrors({
        submit: error.response?.data?.error || 'Failed to check in item',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      returnCondition: 'good',
      returnNotes: 'returned',
    });
    setErrors({});
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    checkinMutation.mutate({
      checkout_id: checkout.checkout_id,
      return_condition: formData.returnCondition,
      return_notes: formData.returnNotes.trim() || undefined,
    });
  };

  const handleClose = () => {
    if (!checkinMutation.isPending) {
      resetForm();
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Check In Item"
      size="md"
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={checkinMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={checkinMutation.isPending}
          >
            {checkinMutation.isPending ? 'Checking in...' : 'Check In'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Checkout Details */}
        <div className="bg-gray-50 p-4 rounded-md space-y-2">
          <div>
            <p className="text-sm text-gray-600">Item</p>
            <p className="font-semibold">{checkout.item_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Checked out by</p>
            <p className="font-medium">{checkout.full_name} ({checkout.ldap})</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Quantity</p>
              <p className="font-medium">{checkout.quantity}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Checkout Date</p>
              <p className="font-medium text-sm">
                {format(new Date(checkout.checkout_date), 'MM/dd/yyyy')}
              </p>
            </div>
          </div>
          {checkout.is_overdue && (
            <div className="pt-2 border-t">
              <p className="text-sm text-red-600 font-medium">
                This item is {checkout.days_overdue} days overdue
              </p>
            </div>
          )}
        </div>

        {/* Return Condition */}
        <div>
          <label htmlFor="returnCondition" className="block text-sm font-medium text-gray-700 mb-1">
            Return Condition <span className="text-red-500">*</span>
          </label>
          <select
            id="returnCondition"
            value={formData.returnCondition}
            onChange={(e) => setFormData({ ...formData, returnCondition: e.target.value as 'good' | 'fair' | 'poor' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="good">Good</option>
            <option value="fair">Fair</option>
            <option value="poor">Poor</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Assess the condition of the item being returned
          </p>
        </div>

        {/* Return Notes */}
        <div>
          <label htmlFor="returnNotes" className="block text-sm font-medium text-gray-700 mb-1">
            Return Notes (Optional)
          </label>
          <textarea
            id="returnNotes"
            rows={3}
            placeholder="Add any notes about the return..."
            value={formData.returnNotes}
            onChange={(e) => setFormData({ ...formData, returnNotes: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">
            Document any damage, issues, or observations
          </p>
        </div>

        {errors.submit && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
      </form>
    </Modal>
  );
};