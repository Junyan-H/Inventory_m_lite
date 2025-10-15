import React from 'react';
import { Link } from 'react-router-dom';
import { Card, Badge } from '@/components/ui';
import type { Item } from '@/types';

interface ItemCardProps {
  item: Item;
  onCheckout?: (item: Item) => void;
}

export const ItemCard: React.FC<ItemCardProps> = ({ item, onCheckout }) => {
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
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <Link to={`/item/${item.item_id}`} className="hover:text-primary-600">
            <h3 className="text-lg font-semibold text-gray-900">{item.item_name}</h3>
          </Link>
          <p className="text-sm text-gray-500 capitalize">{item.category}</p>
        </div>
        {getAvailabilityBadge()}
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Available:</span>
          <span className="font-medium">
            {item.quantity_available} of {item.quantity_total}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Checked Out:</span>
          <span className="font-medium">{item.quantity_checked_out}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Condition:</span>
          <span className="font-medium capitalize">{item.condition}</span>
        </div>
        {item.purchase_price && (
          <div className="flex justify-between">
            <span className="text-gray-600">Price:</span>
            <span className="font-medium">${item.purchase_price.toFixed(2)}</span>
          </div>
        )}
      </div>

      {item.notes && (
        <p className="mt-3 text-sm text-gray-600 border-t pt-3">{item.notes}</p>
      )}

      <div className="mt-4 flex space-x-2">
        <Link
          to={`/item/${item.item_id}`}
          className="flex-1 text-center btn-secondary text-sm py-2"
        >
          View Details
        </Link>
        {item.quantity_available > 0 && onCheckout && (
          <button
            onClick={() => onCheckout(item)}
            className="flex-1 btn-primary text-sm py-2"
          >
            Checkout
          </button>
        )}
      </div>
    </Card>
  );
};