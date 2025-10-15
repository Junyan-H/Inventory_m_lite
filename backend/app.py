import os

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from routes.inventory_routes import home_bp
from routes.checkout_routes import checkout_bp
import database

'''
main flask application
factory pattern with blueprints
'''


def create_app(config_name=None):
    '''
    Application factory pattern

    Args:
        config_name (str): Configuration name ('development', 'production', 'test')
            If None, defaults to FLASK_ENV var

    Returns:
        Flask app instance
    '''

    app = Flask(__name__)

    # Load configurations
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Configure CORS to allow frontend access
    # Allow all origins in development (for troubleshooting)
    CORS(app,
         origins=["http://localhost:3001", "http://localhost:3000"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


    # Initialize database connection pool
    database.init_app(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(checkout_bp)

    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'name': 'Inventory Management API',
            'version': '1.0.0',
            'description': 'RESTful API for equipment inventory checkout system',
            'endpoints': {
                'inventory': {
                    'get_inventory': 'GET /api/inventory?location={location}&ldap={ldap}',
                    'search': 'GET /api/inventory/search?q={query}&location={location}',
                    'get_item': 'GET /api/inventory/{item_id}'
                },
                'checkout': {
                    'checkout': 'POST /api/checkout',
                    'checkin': 'POST /api/checkout/checkin',
                    'active': 'GET /api/checkout/active',
                    'overdue': 'GET /api/checkout/overdue',
                    'user_history': 'GET /api/checkout/user/{ldap}',
                    'item_history': 'GET /api/checkout/item/{item_id}/history'
                }
            }
        }), 200

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=8000, debug=True)
