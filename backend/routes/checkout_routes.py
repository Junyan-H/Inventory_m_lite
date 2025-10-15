"""
Checkout routes for checking equipment in and out
Handles checkout, check-in, and viewing active/historical checkouts
"""

from flask import Blueprint, jsonify, request
from models.checkout import Checkout
from models.user import User
from datetime import datetime

checkout_bp = Blueprint('checkout_bp', __name__, url_prefix='/api/checkout')


@checkout_bp.route('', methods=['POST'])
def checkout_item():
    """
    Check out an item to a user

    Request Body (JSON):
        {
            "item_id": 1,
            "user_ldap": "jhuang",  # or "user_id": 1
            "quantity": 2,
            "expected_return_datetime": "2024-10-20T18:00:00",  # optional, defaults to 8 hours 30 min
            "checkout_condition": "good",  # optional
            "notes": "Field work at client site"  # optional
        }

    Returns:
        JSON response with checkout details

    Example:
        POST /api/checkout
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        item_id = data.get('item_id')
        user_ldap = data.get('user_ldap')
        user_id = data.get('user_id')
        quantity = data.get('quantity', 1)

        if not item_id:
            return jsonify({'error': 'item_id is required'}), 400

        if not user_ldap and not user_id:
            return jsonify({'error': 'Either user_ldap or user_id is required'}), 400

        # Get user ID from LDAP if provided
        if user_ldap and not user_id:
            user = User.get_by_ldap(user_ldap)
            if not user:
                return jsonify({'error': f'User with LDAP {user_ldap} not found'}), 404
            user_id = user['user_id']

        # Optional fields
        expected_return = data.get('expected_return_datetime')
        if expected_return:
            expected_return = datetime.fromisoformat(expected_return.replace('Z', '+00:00'))

        checkout_condition = data.get('checkout_condition', 'good')
        notes = data.get('notes')

        # Perform checkout
        checkout_record = Checkout.checkout_item(
            item_id=item_id,
            user_id=user_id,
            quantity=quantity,
            expected_return_datetime=expected_return,
            checkout_condition=checkout_condition,
            notes=notes
        )

        return jsonify({
            'success': True,
            'message': 'Item checked out successfully',
            'checkout': {
                'checkout_id': checkout_record['checkout_id'],
                'item_id': checkout_record['item_id'],
                'user_id': checkout_record['user_id'],
                'quantity': checkout_record['quantity'],
                'checkout_date': checkout_record['checkout_date'].isoformat(),
                'expected_return_datetime': checkout_record['expected_return_datetime'].isoformat(),
                'checkout_condition': checkout_record['checkout_condition'],
                'notes': checkout_record['notes']
            }
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Checkout failed: {str(e)}'}), 500


@checkout_bp.route('/checkin', methods=['POST'])
def checkin_item():
    """
    Check in an item (return it)

    Request Body (JSON):
        {
            "checkout_id": 1,
            "return_condition": "good",  # optional
            "return_notes": "Returned in good condition"  # optional
        }

    Returns:
        JSON response with checkin details

    Example:
        POST /api/checkout/checkin
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        checkout_id = data.get('checkout_id')
        if not checkout_id:
            return jsonify({'error': 'checkout_id is required'}), 400

        return_condition = data.get('return_condition', 'good')
        return_notes = data.get('return_notes')

        # Perform check-in
        history_record = Checkout.checkin_item(
            checkout_id=checkout_id,
            return_condition=return_condition,
            return_notes=return_notes
        )

        return jsonify({
            'success': True,
            'message': 'Item checked in successfully',
            'history': {
                'history_id': history_record['history_id'],
                'item_id': history_record['item_id'],
                'user_id': history_record['user_id'],
                'quantity': history_record['quantity'],
                'checkout_date': history_record['checkout_date'].isoformat(),
                'return_date': history_record['return_date'].isoformat(),
                'is_returned': history_record['is_returned'],
                'late_return': history_record['late_return'],
                'checkout_condition': history_record['checkout_condition'],
                'return_condition': history_record['return_condition']
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Check-in failed: {str(e)}'}), 500


@checkout_bp.route('/active', methods=['GET'])
def get_active_checkouts():
    """
    Get all active checkouts

    Query Parameters:
        user_id (int, optional): Filter by user
        item_id (int, optional): Filter by item

    Returns:
        JSON response with active checkouts

    Example:
        GET /api/checkout/active?user_id=1
    """
    try:
        user_id = request.args.get('user_id', type=int)
        item_id = request.args.get('item_id', type=int)

        checkouts = Checkout.get_active_checkouts(user_id=user_id, item_id=item_id)

        return jsonify({
            'success': True,
            'total_active_checkouts': len(checkouts),
            'checkouts': [{
                'checkout_id': c['checkout_id'],
                'checkout_date': c['checkout_date'].isoformat(),
                'expected_return_datetime': c['expected_return_datetime'].isoformat() if c['expected_return_datetime'] else None,
                'quantity': c['quantity'],
                'ldap': c['ldap'],
                'full_name': c['full_name'],
                'email': c['email'],
                'item_id': c['item_id'],
                'item_name': c['item_name'],
                'category': c['category'],
                'location': c['location'],
                'is_overdue': c['is_overdue'],
                'days_overdue': c['days_overdue'],
                'notes': c['notes']
            } for c in checkouts]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get active checkouts: {str(e)}'}), 500


@checkout_bp.route('/overdue', methods=['GET'])
def get_overdue_checkouts():
    """
    Get all overdue checkouts

    Returns:
        JSON response with overdue checkouts

    Example:
        GET /api/checkout/overdue
    """
    try:
        checkouts = Checkout.get_overdue_checkouts()

        return jsonify({
            'success': True,
            'total_overdue': len(checkouts),
            'checkouts': [{
                'checkout_id': c['checkout_id'],
                'checkout_date': c['checkout_date'].isoformat(),
                'expected_return_datetime': c['expected_return_datetime'].isoformat() if c['expected_return_datetime'] else None,
                'days_overdue': c['days_overdue'],
                'quantity': c['quantity'],
                'ldap': c['ldap'],
                'full_name': c['full_name'],
                'email': c['email'],
                'item_id': c['item_id'],
                'item_name': c['item_name'],
                'location': c['location']
            } for c in checkouts]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get overdue checkouts: {str(e)}'}), 500


@checkout_bp.route('/user/<string:ldap>', methods=['GET'])
def get_user_checkouts(ldap):
    """
    Get checkout history for a specific user (by LDAP)

    Path Parameters:
        ldap (str): User LDAP username

    Query Parameters:
        limit (int, optional): Max results (default: 50)

    Returns:
        JSON response with user's checkout history

    Example:
        GET /api/checkout/user/jhuang?limit=20
    """
    try:
        # Get user
        user = User.get_by_ldap(ldap)
        if not user:
            return jsonify({'error': f'User {ldap} not found'}), 404

        limit = request.args.get('limit', default=50, type=int)

        history = Checkout.get_user_checkout_history(user['user_id'], limit=limit)

        return jsonify({
            'success': True,
            'user': {
                'ldap': user['ldap'],
                'full_name': user['full_name']
            },
            'total_records': len(history),
            'history': [{
                'history_id': h['history_id'],
                'checkout_date': h['checkout_date'].isoformat(),
                'return_date': h['return_date'].isoformat() if h['return_date'] else None,
                'expected_return_datetime': h['expected_return_datetime'].isoformat() if h['expected_return_datetime'] else None,
                'quantity': h['quantity'],
                'is_returned': h['is_returned'],
                'late_return': h['late_return'],
                'item_id': h['item_id'],
                'item_name': h['item_name'],
                'category': h['category'],
                'location': h['location'],
                'checkout_condition': h['checkout_condition'],
                'return_condition': h['return_condition']
            } for h in history]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get user checkout history: {str(e)}'}), 500


@checkout_bp.route('/item/<int:item_id>/history', methods=['GET'])
def get_item_history(item_id):
    """
    Get checkout history for a specific item

    Path Parameters:
        item_id (int): Item ID

    Query Parameters:
        limit (int, optional): Max results (default: 50)

    Returns:
        JSON response with item's checkout history

    Example:
        GET /api/checkout/item/1/history?limit=20
    """
    try:
        limit = request.args.get('limit', default=50, type=int)

        history = Checkout.get_item_checkout_history(item_id, limit=limit)

        return jsonify({
            'success': True,
            'item_id': item_id,
            'total_records': len(history),
            'history': [{
                'history_id': h['history_id'],
                'checkout_date': h['checkout_date'].isoformat(),
                'return_date': h['return_date'].isoformat() if h['return_date'] else None,
                'expected_return_datetime': h['expected_return_datetime'].isoformat() if h['expected_return_datetime'] else None,
                'quantity': h['quantity'],
                'is_returned': h['is_returned'],
                'late_return': h['late_return'],
                'ldap': h['ldap'],
                'full_name': h['full_name'],
                'checkout_condition': h['checkout_condition'],
                'return_condition': h['return_condition'],
                'checkout_notes': h['checkout_notes'],
                'return_notes': h['return_notes']
            } for h in history]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get item checkout history: {str(e)}'}), 500