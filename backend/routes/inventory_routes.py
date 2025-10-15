"""
Inventory routes for displaying equipment inventory by location
Home page endpoint - displays current inventory for specific location
"""



from flask import Blueprint, jsonify, request
import os
import sys


from models.item import Item
from models.user import User


home_bp = Blueprint('home_bp', __name__, url_prefix='/api/inventory')


@home_bp.route('', methods=['GET'])
def get_inventory():
    '''
    Get inventory items for a specific location (Home Page)

    Query Parameters:
        location (str, required): Location name (e.g., 'san_jose', '2u', '3k')
        ldap (str, optional): User LDAP for authentication

    Returns:
        JSON response with items and availability

    Example:
        GET /api/inventory?location=san_jose&ldap=jhuang
    '''

    # Get query parameters
    location = request.args.get('location', '').strip()
    ldap = request.args.get('ldap', '').strip()

    # Validate required parameters
    if not location:
        return jsonify({
            'error': 'Missing required parameter: location'
        }), 400

    # Optional: Validate location against allowed locations
    locations_str = os.environ.get('LOCATIONS', '')
    if locations_str and location not in locations_str:
        return jsonify({
            'error': 'Invalid location',
            'valid_locations': locations_str
        }), 400

    # Optional: Validate and get user info
    user = None
    if ldap:
        user = User.get_by_ldap(ldap)
        if not user:
            return jsonify({
                'error': 'Invalid LDAP username'
            }), 401

    try:
        # Query inventory from database
        items = Item.get_by_location(location)

        # Format response
        response_items = []
        for item in items:
            response_items.append({
                'item_id': item['item_id'],
                'item_name': item['item_name'],
                'category': item['category'],
                'location': item['location'],
                'quantity_total': item['quantity_total'],
                'quantity_available': item['quantity_available'],
                'quantity_checked_out': item['quantity_checked_out'],
                'purchase_price': float(item['purchase_price']) if item['purchase_price'] else None,
                'condition': item['condition'],
                'status': item['status'],
                'notes': item['notes'],
                'image_url': item['image_url'],
                'availability_status': (
                    'Out of Stock' if item['quantity_available'] == 0
                    else 'Low Stock' if item['quantity_available'] < (item['quantity_total'] * 0.2)
                    else 'Available'
                )
            })

        return jsonify({
            'success': True,
            'location': location,
            'user': {
                'ldap': user['ldap'],
                'full_name': user['full_name']
            } if user else None,
            'total_items': len(response_items),
            'items': response_items
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to load inventory data',
            'details': str(e)
        }), 500


@home_bp.route('/search', methods=['GET'])
def search_inventory():
    '''
    Search inventory items by name or category

    Query Parameters:
        q (str, required): Search query
        location (str, optional): Filter by location

    Returns:
        JSON response with matching items

    Example:
        GET /api/inventory/search?q=drill&location=san_jose
    '''
    query_text = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip() or None

    if not query_text:
        return jsonify({
            'error': 'Missing required parameter: q (search query)'
        }), 400

    try:
        items = Item.search(query_text, location)

        response_items = [{
            'item_id': item['item_id'],
            'item_name': item['item_name'],
            'category': item['category'],
            'location': item['location'],
            'quantity_available': item['quantity_available'],
            'condition': item['condition'],
            'status': item['status']
        } for item in items]

        return jsonify({
            'success': True,
            'query': query_text,
            'location': location,
            'total_results': len(response_items),
            'items': response_items
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Search failed',
            'details': str(e)
        }), 500


@home_bp.route('/<int:item_id>', methods=['GET'])
def get_item_details(item_id):
    '''
    Get detailed information for a specific item

    Path Parameters:
        item_id (int): Item ID

    Returns:
        JSON response with item details

    Example:
        GET /api/inventory/42
    '''
    try:


        item = Item.get_by_id(item_id)

        if not item:
            return jsonify({
                'error': 'Item not found'
            }), 404

        return jsonify({
            'success': True,
            'item': {
                'item_id': item['item_id'],
                'item_name': item['item_name'],
                'category': item['category'],
                'location': item['location'],
                'quantity_total': item['quantity_total'],
                'quantity_available': item['quantity_available'],
                'quantity_checked_out': item['quantity_checked_out'],
                'purchase_price': float(item['purchase_price']) if item['purchase_price'] else None,
                'restock_date': item['restock_date'].isoformat() if item['restock_date'] else None,
                'condition': item['condition'],
                'status': item['status'],
                'last_audit_date': item['last_audit_date'].isoformat() if item['last_audit_date'] else None,
                'notes': item['notes'],
                'image_url': item['image_url']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get item details',
            'details': str(e)
        }), 500
