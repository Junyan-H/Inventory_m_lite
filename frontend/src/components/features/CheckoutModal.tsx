import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal, Button, Input } from '@/components/ui';
import { checkoutItem } from '@/api';
import type { Item } from '@/types';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: Item;
}

export const CheckoutModal: React.FC<CheckoutModalProps> = ({
  isOpen,
  onClose,
  item,
}) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    ldap: '',
    quantity: 1,
    expectedReturn: '',
    condition: 'good' as const,
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const checkoutMutation = useMutation({
    mutationFn: checkoutItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['item', item.item_id] });
      queryClient.invalidateQueries({ queryKey: ['item-history', item.item_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['active-checkouts'] });
      onClose();
      resetForm();
    },
    onError: (error: any) => {
      setErrors({
        submit: error.response?.data?.error || 'Failed to checkout item',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      ldap: '',
      quantity: 1,
      expectedReturn: '',
      condition: 'good',
      notes: '',
    });
    setErrors({});
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.ldap.trim()) {
      newErrors.ldap = 'LDAP username is required';
    }

    if (formData.quantity < 1) {
      newErrors.quantity = 'Quantity must be at least 1';
    } else if (formData.quantity > item.quantity_available) {
      newErrors.quantity = `Only ${item.quantity_available} available`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    checkoutMutation.mutate({
      item_id: item.item_id,
      user_ldap: formData.ldap.trim(),
      quantity: formData.quantity,
      expected_return_datetime: formData.expectedReturn || undefined,
      checkout_condition: formData.condition,
      notes: formData.notes.trim() || undefined,
    });
  };

  const handleClose = () => {
    if (!checkoutMutation.isPending) {
      resetForm();
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Checkout Item"
      size="md"
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={checkoutMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={checkoutMutation.isPending}
          >
            {checkoutMutation.isPending ? 'Checking out...' : 'Checkout'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-4">
            Checking out: <span className="font-semibold">{item.item_name}</span>
          </p>
          <p className="text-sm text-gray-600 mb-4">
            Available quantity: <span className="font-semibold">{item.quantity_available}</span>
          </p>
        </div>

        {/* LDAP Field */}
        <div>
          <label htmlFor="ldap" className="block text-sm font-medium text-gray-700 mb-1">
            LDAP Username <span className="text-red-500">*</span>
          </label>
          <Input
            id="ldap"
            type="text"
            placeholder="Enter LDAP username"
            value={formData.ldap}
            onChange={(e) => setFormData({ ...formData, ldap: e.target.value })}
            className={errors.ldap ? 'border-red-500' : ''}
          />
          {errors.ldap && (
            <p className="text-sm text-red-600 mt-1">{errors.ldap}</p>
          )}
        </div>

        {/* Quantity Field */}
        <div>
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
            Quantity <span className="text-red-500">*</span>
          </label>
          <Input
            id="quantity"
            type="number"
            min="1"
            max={item.quantity_available}
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 1 })}
            className={errors.quantity ? 'border-red-500' : ''}
          />
          {errors.quantity && (
            <p className="text-sm text-red-600 mt-1">{errors.quantity}</p>
          )}
        </div>

        {/* Expected Return Date */}
        <div>
          <label htmlFor="expectedReturn" className="block text-sm font-medium text-gray-700 mb-1">
            Expected Return Date (Optional)
          </label>
          <Input
            id="expectedReturn"
            type="datetime-local"
            value={formData.expectedReturn}
            onChange={(e) => setFormData({ ...formData, expectedReturn: e.target.value })}
          />
          <p className="text-xs text-gray-500 mt-1">
            If not specified, defaults to 7 days from now
          </p>
        </div>

        {/* Condition */}
        <div>
          <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-1">
            Item Condition
          </label>
          <select
            id="condition"
            value={formData.condition}
            onChange={(e) => setFormData({ ...formData, condition: e.target.value as 'good' | 'fair' | 'poor' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="good">Good</option>
            <option value="fair">Fair</option>
            <option value="poor">Poor</option>
          </select>
        </div>

        {/* Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            Notes (Optional)
          </label>
          <textarea
            id="notes"
            rows={3}
            placeholder="Add any notes about this checkout..."
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
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